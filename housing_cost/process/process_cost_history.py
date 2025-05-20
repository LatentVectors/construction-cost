from pathlib import Path
import re

import cpi  # type: ignore
import pandas as pd


def process_cost_history(path: Path, target_year: int = 2024) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Process the cost history data from a CSV file.

    Args:
        path (Path): The path to the CSV file containing the cost history data.
        target_year (int): The year to adjust the cost history to.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the processed cost history
        data and the dollar value of each category.
    """

    def clean_name(name: str) -> str:
        """"""
        name = name.strip()
        match = re.match(r"^\d+\.\s*(.*)$", name)
        if match:
            name = match.group(1).strip()
        return name

    def clean_values(value: str) -> float | None:
        """"""
        value = re.sub(r'["\s\$,%]', "", value)
        if value == "":
            return None
        return float(value)

    df = pd.read_csv(path)
    df.columns = pd.Index(["category", *df.columns[1:]])
    df["category"] = df["category"].apply(clean_name)
    df = df.melt(id_vars=["category"], var_name="year", value_name="value")
    df = df.pivot(columns="category", index="year", values="value")
    df = df.map(clean_values)  # type: ignore
    df["percent_total"] = df[df.columns[:-1]].sum(axis=1)

    # Dollar value of each category
    dfc = df.copy()
    for col in dfc.columns[:-2]:
        dfc[col] = (dfc[col] / dfc["percent_total"]) * dfc["Total Sales Price ($)"]
    dfc["total"] = dfc[dfc.columns[:-2]].sum(axis=1)
    dfc = dfc.round(0).astype(int)
    dfc["difference"] = dfc["total"] - dfc["Total Sales Price ($)"]

    dfc = dfc.drop(columns=["difference", "percent_total", "total", "Total Sales Price ($)"])
    dfc = dfc[dfc.mean().sort_values(ascending=False).index]
    df = df.reset_index().melt(id_vars=["year"], var_name="category", value_name="percent")
    dfc = dfc.reset_index().melt(id_vars=["year"], var_name="category", value_name="value")
    years = {int(y): cpi.get(int(y)) for y in df["year"].unique()}
    max_cpi = cpi.get(target_year)
    dfc["cpi"] = dfc["year"].apply(lambda x: years[int(x)])
    dfc["usd_adjusted"] = dfc["value"] * (max_cpi / dfc["cpi"])
    dfc = dfc[["year", "category", "value", "usd_adjusted"]]
    dfc.columns = pd.Index(["year", "category", "usd", "usd_adjusted"])
    return df, dfc
