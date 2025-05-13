from pathlib import Path
import re
from typing import Tuple

import pandas as pd


def process_construction_cost_2024(filepath: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Process the construction cost 2024 data.

    Args:
        filepath: The path to the construction cost 2024 data.

    Returns:
        A tuple of two DataFrames:
            - The first DataFrame contains the totals.
            - The second DataFrame contains the subtotals.
    """
    df = pd.read_csv(filepath)
    df.columns = pd.Index(["name", "cost", "percent"])

    def is_total(name: str) -> bool:
        """Return true if the name is a category."""
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
        return any(name.startswith(stub) for stub in category_stubs)

    def clean_name(name: str) -> str | None:
        """Return the name of the category."""
        name = re.sub(r"\(sum.*\)", "", name)
        match = re.match(r"^[A-Z]+\. (.*)$", name)
        if match:
            return match.group(1).strip()
        return name.strip()

    def clean_cost(value: str) -> int:
        """Clean the cost of the item."""
        return int(value.replace("$", "").replace(",", "").replace(" ", ""))

    def clean_percent(value: str) -> float:
        """Clean the percent of the item."""
        return float(value.replace("%", "").replace(" ", ""))

    df["is_total"] = df["name"].apply(is_total)
    df["subcategory"] = df["name"].apply(clean_name)
    df["category"] = df["subcategory"].where(df["is_total"], None)
    df["category"] = df["category"].ffill()
    df["cost"] = df["cost"].apply(clean_cost)
    df["percent"] = df["percent"].apply(clean_percent)
    df = df[["category", "subcategory", "cost", "percent", "is_total"]]

    totals = df[df["is_total"]]
    totals = totals.drop(columns=["subcategory"])
    totals = totals.set_index(["category"])

    subtotals = df[~df["is_total"]]
    subtotals = subtotals.set_index(["category", "subcategory"])

    return totals, subtotals
