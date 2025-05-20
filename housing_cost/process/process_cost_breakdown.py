# %%
import re

import cpi  # type: ignore
import pandas as pd

from housing_cost.config import INTERIM_DATA_DIR

cpi.update()
# %%
COST = "cost"
YEAR = "year"
PERCENT = "percent"
CATEGORY = "category"
SUBCATEGORY = "subcategory"
IS_TOTAL = "is_total"
USD = "usd"
USD_ADJUSTED = "usd_adjusted"
CPI = "cpi_index"
SQR_FEET = "sqr_feet"
LOT_SIZE = "lot_size"


def process_cost_breakdown() -> pd.DataFrame:
    """Process the cost breakdown data for the 2024 NABH Construction Cost Survey."""
    part_1_path = INTERIM_DATA_DIR / "NABH Construction Cost - 2024__table_7__values.csv"
    part_2_path = INTERIM_DATA_DIR / "NABH Construction Cost - 2024__table_8__values.csv"

    df1 = pd.read_csv(part_1_path)
    df2 = pd.read_csv(part_2_path)

    df1 = pd.melt(df1, id_vars=[df1.columns[0]], var_name=YEAR, value_name=PERCENT)
    df2 = pd.melt(df2, id_vars=[df2.columns[0]], var_name=YEAR, value_name=PERCENT)
    df = pd.concat([df1, df2])
    df.columns = pd.Index([COST, YEAR, PERCENT])

    # I hard coded these values because the PDF parser did not extract them correctly.
    # They are formatted vertically which appears to confuse the parser.
    df_total = pd.DataFrame(
        {
            1998: {
                USD: 124276,
            },
            2002: {
                USD: 151671,
            },
            2004: {
                USD: 192846,
            },
            2007: {
                USD: 219015,
            },
            2009: {
                SQR_FEET: 2716,
                LOT_SIZE: 21879,
                USD: 222511,
            },
            2011: {
                SQR_FEET: 2311,
                LOT_SIZE: 20614,
                USD: 184125,
            },
            2013: {
                SQR_FEET: 2607,
                LOT_SIZE: 14359,
                USD: 246453,
            },
            2015: {
                SQR_FEET: 2802,
                LOT_SIZE: 20129,
                USD: 289415,
            },
            2017: {
                SQR_FEET: 2776,
                LOT_SIZE: 11186,
                USD: 237760,
            },
            2019: {
                SQR_FEET: 2594,
                LOT_SIZE: 22094,
                USD: 296792,
            },
            2022: {
                SQR_FEET: 2561,
                LOT_SIZE: 17218,
                USD: 392241,
            },
            2024: {
                SQR_FEET: 2647,
                LOT_SIZE: 20907,
                USD: 428215,
            },
        }
    ).T.reset_index()
    df_total.columns = pd.Index([YEAR, USD, SQR_FEET, LOT_SIZE])

    df_total[CPI] = df_total[YEAR].apply(lambda x: cpi.get(x))
    last_year = df_total[YEAR].max()
    df_total[USD_ADJUSTED] = df_total[USD] * (cpi.get(last_year) / df_total[CPI])

    def is_total(name: str) -> bool:
        """Return true if the name is a category."""
        name = name.lower().strip()
        category_stubs = [
            "I. Site Work",
            "II. Foundations",
            "III. Framing",
            "IV. Exterior Finishes",
            "V. Major Systems",
            "VI. Interior Finishes",
            "VII. Final Steps",
            "VIII. Other",
            "Total",
        ]
        return any(name.startswith(stub.lower()) for stub in category_stubs)

    def clean_name(name: str) -> str | None:
        """Return the name of the category."""
        name = re.sub(r"\(sum.*\)", "", name)
        match = re.match(r"^[A-Z]+\. (.*)$", name)
        if match:
            return match.group(1).strip()
        return name.strip()

    def clean_percent(percent: str) -> float | None:
        """Return the percent of the category."""
        if isinstance(percent, float):
            return percent
        if isinstance(percent, str):
            match = re.match(r"(\d+\.?\d*)%", percent)
            if match:
                return float(match.group(1))
        return None

    labels = df[COST].value_counts().to_frame().reset_index()
    labels[IS_TOTAL] = labels[COST].apply(is_total)
    labels[SUBCATEGORY] = labels[COST].apply(clean_name)
    labels[CATEGORY] = labels[SUBCATEGORY].where(labels[IS_TOTAL], None)
    labels[CATEGORY] = labels[CATEGORY].ffill()
    labels.set_index(COST, inplace=True)

    df.set_index(COST, inplace=True)
    df = df.join(labels).reset_index(drop=True)
    df = df.drop(columns=["count"])
    df[YEAR] = df[YEAR].astype("Int32")
    df[PERCENT] = df[PERCENT].apply(clean_percent)
    df = df.merge(df_total, on=YEAR)
    df.set_index([CATEGORY, SUBCATEGORY, YEAR], inplace=True)
    return df
