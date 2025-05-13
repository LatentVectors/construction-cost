from pathlib import Path
import time  # Added for polling delay
from typing import Dict, List, Optional, Tuple, Union

from loguru import logger
from mypy_boto3_s3.client import S3Client
from mypy_boto3_textract.client import TextractClient
from mypy_boto3_textract.type_defs import (
    BlockTypeDef,
    GetDocumentAnalysisRequestTypeDef,
    GetDocumentAnalysisResponseTypeDef,
    StartDocumentAnalysisRequestTypeDef,
    StartDocumentAnalysisResponseTypeDef,
)


def extract_pdf_tables(
    textract_client: TextractClient,
    s3_client: S3Client,
    s3_bucket_name: str,
    filepaths: List[Path],
    output_dir: Path,
) -> str:
    """Extract the tables from PDF files using asynchronous processing.
    Manages uploading local files to S3 and removing them after processing.
    Saves CSV results to the output_dir.
    """
    # Get the region from the Textract client
    region_name = textract_client.meta.region_name

    # Create bucket if it doesn't exist
    try:
        s3_client.create_bucket(
            Bucket=s3_bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region_name},  # type: ignore
        )
    except s3_client.exceptions.BucketAlreadyExists:
        logger.info(f"Bucket {s3_bucket_name} already exists")
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        logger.info(f"Bucket {s3_bucket_name} already owned by you")

    results_summary: List[str] = []

    output_dir.mkdir(parents=True, exist_ok=True)

    for file_path in filepaths:
        s3_object_name = file_path.name

        current_file_summary_prefix = f"Processing {file_path.name}:"
        logger.info(current_file_summary_prefix)

        try:
            # Upload the file to S3
            print(f"  Uploading {file_path} to s3://{s3_bucket_name}/{s3_object_name}")
            s3_client.upload_file(str(file_path), s3_bucket_name, s3_object_name)
            print(f"  Upload of {s3_object_name} complete.")

            # Process the file using Textract
            results = get_table_csv_results(textract_client, s3_bucket_name, s3_object_name)

            # Save the CSV data
            if results is None:
                logger.info(f" - No tables found in {file_path.name}")
            else:
                for table_index, (csv, scores_csv) in results.items():
                    values_csv_path = output_dir / (
                        file_path.stem + f"__table_{table_index}__values.csv"
                    )
                    scores_csv_path = output_dir / (
                        file_path.stem + f"__table_{table_index}__scores.csv"
                    )

                    with open(values_csv_path, "w") as f:
                        f.write(csv)

                    with open(scores_csv_path, "w") as f:
                        f.write(scores_csv)

        except Exception as e:
            error_msg = f"  - Error processing {file_path.name}: {e}"
            logger.error(error_msg)
            results_summary.append(f"{current_file_summary_prefix}\n{error_msg}")
        finally:
            # Ensure the file is deleted from S3 after processing
            try:
                logger.info(f"  Deleting s3://{s3_bucket_name}/{s3_object_name} from S3.")
                s3_client.delete_object(Bucket=s3_bucket_name, Key=s3_object_name)
                logger.info(f"  Deletion of {s3_object_name} from S3 complete.")
            except Exception as e_del:
                delete_error_msg = f"  - Error deleting {s3_object_name} from S3: {e_del}"
                logger.error(delete_error_msg)
                # Append to the *last* entry in results_summary related to this file, or just print
                if results_summary and results_summary[-1].startswith(current_file_summary_prefix):
                    results_summary[-1] += f"\n{delete_error_msg}"
                else:  # Should not happen if processing started
                    results_summary.append(f"{current_file_summary_prefix}\n{delete_error_msg}")

    s3_client.delete_bucket(Bucket=s3_bucket_name)
    return "\n---\n".join(results_summary)


def get_table_csv_results(
    client: TextractClient, s3_bucket_name: str, s3_object_name: str
) -> Union[dict[int, Tuple[str, str]], None]:
    """Get the table csv results from the PDF file using asynchronous processing."""
    logger.info(f"Starting Textract job for s3://{s3_bucket_name}/{s3_object_name}")

    # Start the document analysis job
    start_job_request: StartDocumentAnalysisRequestTypeDef = {
        "DocumentLocation": {"S3Object": {"Bucket": s3_bucket_name, "Name": s3_object_name}},
        "FeatureTypes": ["TABLES"],
    }
    start_job_response: StartDocumentAnalysisResponseTypeDef = client.start_document_analysis(
        **start_job_request
    )
    job_id: str = start_job_response["JobId"]
    logger.info(f"Job started with ID: {job_id}")

    # Poll for job completion
    job_status: str = "IN_PROGRESS"
    get_job_response: GetDocumentAnalysisResponseTypeDef
    pages_processed: int = 0

    while job_status == "IN_PROGRESS" or job_status == "PARTIAL_SUCCESS":
        time.sleep(5)  # Poll every 5 seconds
        get_job_request: GetDocumentAnalysisRequestTypeDef = {"JobId": job_id}
        get_job_response = client.get_document_analysis(**get_job_request)
        job_status = get_job_response["JobStatus"]
        if "StatusMessage" in get_job_response:
            logger.info(f"Job status: {job_status} - {get_job_response['StatusMessage']}")
        else:
            logger.info(f"Job status: {job_status}")

        # Check if document metadata and pages are available
        if (
            "DocumentMetadata" in get_job_response
            and "Pages" in get_job_response["DocumentMetadata"]
        ):
            current_pages_processed = get_job_response["DocumentMetadata"]["Pages"]
            if current_pages_processed != pages_processed:
                pages_processed = current_pages_processed
                logger.info(f"Pages processed: {pages_processed}")

    if job_status != "SUCCEEDED":
        error_message = f"Textract job failed with status: {job_status}."
        if "StatusMessage" in get_job_response:
            error_message += f" Message: {get_job_response['StatusMessage']}"
        if "Warnings" in get_job_response:
            error_message += f" Warnings: {get_job_response['Warnings']}"
        logger.error(error_message)
        return None

    # Get the results
    blocks: List[BlockTypeDef] = []
    next_token: Optional[str] = None

    # Paginate through results if necessary
    while True:
        get_job_request_final: GetDocumentAnalysisRequestTypeDef = {"JobId": job_id}
        if next_token:
            get_job_request_final["NextToken"] = next_token

        final_response = client.get_document_analysis(**get_job_request_final)

        blocks.extend(final_response["Blocks"])

        next_token = final_response.get("NextToken")
        if not next_token:
            break

    logger.info(f"Total blocks received: {len(blocks)}")
    # pprint(blocks) # Commented out for brevity, can be re-enabled for debugging

    blocks_map: Dict[str, BlockTypeDef] = {}
    table_blocks: List[BlockTypeDef] = []
    for block in blocks:
        blocks_map[block["Id"]] = block
        if block["BlockType"] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) <= 0:
        logger.warning("No tables found in the document.")
        return None

    results: dict[int, Tuple[str, str]] = {}
    for index, table in enumerate(table_blocks):
        csv, scores_csv = generate_table_csv(table, blocks_map)
        results[index + 1] = (csv, scores_csv)

    return results


def generate_table_csv(
    table_result: BlockTypeDef, blocks_map: Dict[str, BlockTypeDef]
) -> Tuple[str, str]:
    """Generate the table csv from the table result."""
    rows: Dict[int, Dict[int, str]]
    scores: List[str]
    rows, scores = get_rows_columns_map(table_result, blocks_map)

    # get cells.
    csv: str = ""
    for row_index, cols in rows.items():
        col_indices: int = 0  # Initialize col_indices
        for col_index, text in cols.items():
            col_indices = len(cols.items())
            text = text.replace('"', '""')  # Escape double quotes
            csv += '"{}"'.format(text) + ","
        csv = csv.rstrip(",")  # Remove the trailing comma
        csv += "\n"

    scores_csv: str = ""
    cols_count: int = 0
    # Ensure col_indices is defined if rows is empty
    if not rows:
        col_indices = 0  # Default if there are no columns, to avoid UnboundLocalError

    for score in scores:
        cols_count += 1
        scores_csv += score + ","
        if col_indices > 0 and cols_count == col_indices:  # check col_indices > 0
            scores_csv = scores_csv.rstrip(",")  # Remove the trailing comma
            scores_csv += "\n"
            cols_count = 0

    return csv, scores_csv


def get_rows_columns_map(
    table_result: BlockTypeDef, blocks_map: Dict[str, BlockTypeDef]
) -> Tuple[Dict[int, Dict[int, str]], List[str]]:
    """Get the rows and columns map from the table result."""
    rows: Dict[int, Dict[int, str]] = {}
    scores: List[str] = []
    for relationship in table_result["Relationships"]:
        if relationship["Type"] == "CHILD":
            for child_id in relationship["Ids"]:
                cell: BlockTypeDef = blocks_map[child_id]
                if cell["BlockType"] == "CELL":
                    row_index: int = cell["RowIndex"]
                    col_index: int = cell["ColumnIndex"]
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}

                    # get confidence score
                    scores.append(str(cell["Confidence"]))

                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows, scores


def get_text(result: BlockTypeDef, blocks_map: Dict[str, BlockTypeDef]) -> str:
    """Get the text from the result."""
    text: str = ""
    if "Relationships" in result:
        for relationship in result["Relationships"]:
            if relationship["Type"] == "CHILD":
                for child_id in relationship["Ids"]:
                    word: BlockTypeDef = blocks_map[child_id]
                    if word["BlockType"] == "WORD":
                        if "," in word["Text"] and word["Text"].replace(",", "").isnumeric():
                            text += '"' + word["Text"] + '"' + " "
                        else:
                            text += word["Text"] + " "
                    if word["BlockType"] == "SELECTION_ELEMENT":
                        if word["SelectionStatus"] == "SELECTED":
                            text += "X "
    return text
