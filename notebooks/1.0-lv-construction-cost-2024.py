# %%

import pandas as pd

from housing_cost.config import INTERIM_DATA_DIR
from housing_cost.process.process_construction_cost import process_construction_cost_2024

pd.set_option("display.width", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", None)

construction_cost_2024 = INTERIM_DATA_DIR / "NABH Construction Cost - 2024__table_3__values.csv"


totals, subtotals = process_construction_cost_2024(construction_cost_2024)

print(totals)
print(subtotals)

# %%
print("PARSED DATA VALIDATION\n")
# NOTE: Values many not match perfectly, because the original data had some rounding errors.
# This is intended primarily as a sanity check to make sure the data was parsed correctly.
total_sum = totals[totals.index.get_level_values(0) != "Total"].sum()
totals_row = totals[totals.index.get_level_values(0) == "Total"]
print("Totals Sums:")
print("-" * 80)
print(total_sum)
print(totals_row)
print("cost:\t\t", (total_sum["cost"] - totals_row["cost"]).iloc[0])
print("percent:\t", (total_sum["percent"] - totals_row["percent"]).iloc[0])

subtotal_sum = subtotals.groupby("category")[["cost", "percent"]].sum()
subtotal_sum.columns = pd.Index(["cost_sub", "percent_sub"])
subtotal_sum = pd.concat(
    [subtotal_sum, totals],
    axis=1,
    join="outer",
)
subtotal_sum["cost_tdiff"] = subtotal_sum["cost_sub"] - subtotal_sum["cost"]
subtotal_sum["percent_tdiff"] = subtotal_sum["percent_sub"] - subtotal_sum["percent"]
subtotal_sum = subtotal_sum.drop(columns=["is_total"])
subtotal_sum = subtotal_sum.sort_index(axis=1)
print("\n\nSubtotal Sums:")
print("-" * 80)
print(subtotal_sum)
