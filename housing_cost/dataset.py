import boto3
from loguru import logger
import pandas as pd
import requests
import typer

from housing_cost.config import (
    COST_BREAKDOWN,
    COST_DETAIL_SUBTOTALS,
    COST_DETAIL_TOTALS,
    COST_HISTORY_PERCENT,
    COST_HISTORY_USD,
    INTERIM_DATA_DIR,
    MEDIAN_INCOME,
    RAW_DATA_DIR,
)
from housing_cost.pdf import extract_pdf_tables
from housing_cost.process import (
    process_construction_cost_2024,
    process_cost_breakdown,
    process_cost_history,
    process_median_income,
)

app = typer.Typer()


@app.command()
def main():
    logger.info("Welcome to the Housing Cost Dataset!")


@app.command()
def download():
    """Download the NAHB Construction Cost Survey data."""
    logger.info("Downloading datasets...")
    urls = {
        "Table H-9 - All Households Income.xlsx": "https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-households/h09ar.xlsx",
        "NABH Construction Cost - 2024.pdf": "https://www.nahb.org/-/media/AB4EFC742624475A97A0A62189986FF8.ashx",
        "NABH Construction Cost - 2022.pdf": "https://www.nahb.org/-/media/27E8E24FA6CB432CA4EF3D9C0249771D.ashx",
        "NABH Construction Cost - 2020.pdf": "https://www.nahb.org/-/media/8F04D7F6EAA34DBF8867D7C3385D2977.ashx",
        "NABH Construction Cost - 2017.pdf": "https://www.nahb.org/-/media/CC931183F12F43239FFDA9CD80A06F4D.ashx",
    }
    for filename, url in urls.items():
        logger.info(f"Downloading {filename}...")
        response = requests.get(url, verify=False)
        filepath = RAW_DATA_DIR / filename
        with open(filepath, "wb") as f:
            f.write(response.content)
        logger.success(f"Downloaded {filename}.")
    logger.success("Downloading dataset complete.")


@app.command()
def parse():
    """Extract the tables from the PDF files."""
    session = boto3.Session()
    textract_client = session.client("textract", region_name="us-west-2")
    s3_client = boto3.client("s3", region_name="us-west-2")
    files = [
        RAW_DATA_DIR / "NABH Construction Cost - 2024.pdf",
    ]
    extract_pdf_tables(
        textract_client,
        s3_client,
        "nahb-construction-cost-survey",
        files,
        INTERIM_DATA_DIR,
    )
    logger.success("Extracting tables complete.")


@app.command()
def process():
    """Process the data."""
    logger.info("Processing construction cost...")
    totals, subtotals = process_construction_cost_2024(
        INTERIM_DATA_DIR / "NABH Construction Cost - 2024__table_3__values.csv"
    )
    totals.to_csv(COST_DETAIL_TOTALS)
    subtotals.to_csv(COST_DETAIL_SUBTOTALS)

    logger.info("Processing cost history...")
    part_1_path = INTERIM_DATA_DIR / "NABH Construction Cost - 2024__table_5__values.csv"
    part_2_path = INTERIM_DATA_DIR / "NABH Construction Cost - 2024__table_6__values.csv"
    df_1, dfc_1 = process_cost_history(part_1_path)
    df_2, dfc_2 = process_cost_history(part_2_path)
    df = pd.concat([df_1, df_2])
    dfc = pd.concat([dfc_1, dfc_2])
    df.to_csv(COST_HISTORY_PERCENT)
    dfc.to_csv(COST_HISTORY_USD)

    logger.info("Processing median income...")
    inflation_rate = 1.029
    income_growth_rate = 1.04
    df = process_median_income(
        RAW_DATA_DIR / "Table H-9 - All Households Income.xlsx",
        inflation_rate,
        income_growth_rate,
    )
    df.to_csv(MEDIAN_INCOME)

    logger.info("Processing cost breakdown...")
    df = process_cost_breakdown()
    df.to_csv(COST_BREAKDOWN)


if __name__ == "__main__":
    app()
