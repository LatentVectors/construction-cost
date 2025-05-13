from pathlib import Path
import re
from typing import Any, Tuple

import pandas as pd


def process_median_income(
    filepath: Path, inflation_rate: float, income_growth_rate: float
) -> pd.DataFrame:
    """Process the median income data. Projects the next year's median income.

    Args:
        filepath: The path to the median income data.
        inflation_rate: The inflation rate.
        income_growth_rate: The income growth rate.

    Returns:
        A DataFrame containing the processed median income data.
    """

    def parse_year(value: Any) -> Tuple[int, int | None]:
        """Parse the year and optional footnote from a string."""
        if isinstance(value, int):
            return value, None
        match = re.match(r"^(\d{4})(.*)$", value)
        if match:
            year = int(match.group(1).strip())
            footnote = (
                int(match.group(2).strip().replace("(", "").replace(")", ""))
                if match.group(2)
                else None
            )
            return year, footnote
        if isinstance(value, str):
            return int(value.strip()), None
        raise ValueError(f"Unexpected value: {value}")

    # Limit rows to all households.
    df = pd.read_excel(filepath, skiprows=7, header=[0, 1], nrows=46)
    # NOTE: Households are in thousands.
    df.columns = pd.Index(
        ["year", "households", "median_current", "median_2023", "mean_current", "mean_2023"]
    )
    result = df["year"].apply(parse_year)
    df["year"], df["footnote"] = zip(*result)
    df = df.astype({x: "Int64" for x in df.columns})

    last_year = df["year"].max()
    last_median_income = df.loc[df["year"] == last_year]["median_current"].values[0]
    projected_median_income = last_median_income * income_growth_rate
    projected_median_income_normalized = projected_median_income / inflation_rate

    projected = pd.DataFrame(
        [
            {
                "year": last_year + 1,
                "median_current": int(projected_median_income),
                "median_2023": int(projected_median_income_normalized),
            }
        ]
    )
    df = pd.concat([df, projected])
    df.sort_values(by="year", ascending=False, inplace=True)
    return df
