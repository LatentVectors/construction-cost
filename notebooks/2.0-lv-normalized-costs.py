# %%
import matplotlib.pyplot as plt
import pandas as pd

from housing_cost.config import COST_HISTORY_USD, MEDIAN_INCOME

pd.set_option("display.width", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", None)

df = pd.read_csv(COST_HISTORY_USD)
df.set_index("year", inplace=True)
df_income = pd.read_csv(MEDIAN_INCOME)
df_income.set_index("year", inplace=True)

df_norm = df.copy().div(df_income["median_current"].reindex(df.index), axis=0)
df_norm.plot.line()
plt.show()

df.plot.line()
plt.show()
# %%
"""
In terms of median annual income, 2024 is the the highest year for house costs.
2004, 2007, 2015, and 2022 are all higher than the 2024 level. There are missing
years in the dataset that may also be higher.

The majority of those costs savings appear to be coming from a decrease in 
finished lot size. I am suspicious that this is due to lot sizes shrinking and
home size shrinking.

While there are years where building has been more expensive overall, there is only
a single year in the dataset where construction costs have been higher than 2024 
and only by a small margin.
"""
# TODO: How does lot size cost compare to the size of lots.
# TODO: How does normalized cost per square foot look?
# TODO: Are homes shrinking and getting more expensive?
# TODO: What is construction cost per square foot?
# TODO: What is contributing most to the increase in construction costs?
last_year = df_norm.index.max()
first_year = df_norm.index.min()
all_years = pd.Index(range(first_year, last_year + 1))
df_all = df_norm.reindex(all_years)
y_max = df_all.loc[last_year].sum()
y_construction = df_all.loc[last_year]["Total Construction Cost"]
ax = df_all.plot.bar(stacked=True)
ax.axhline(y_max, color="gray", alpha=0.5)
ax.axhline(y_construction, color="blue", linestyle=":", alpha=0.5)
ax.set_title("House Costs in terms of Median Annual Income")
ax.set_ylabel("Multiple of Median Annual Income")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.show()
# %%

df_all[
    [
        "Overhead and General Expenses",
        # "Sales Commission",
        # "Financing Cost",
        "Marketing Cost",
    ]
].plot.bar(stacked=True)
plt.show()
# %%

ax = df_all[["Marketing Cost"]].dropna().plot.line()
ax.set_title("Marketing Cost")
plt.show()
ax = df_all["Overhead and General Expenses"].dropna().plot.line()
ax.set_title("Overhead and General Expenses")
plt.show()
# %%
