# %%

import matplotlib.pyplot as plt
import pandas as pd

from housing_cost.config import RAW_DATA_DIR
from housing_cost.process.process_median_income import process_median_income

pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

household_income = RAW_DATA_DIR / "Table H-9 - All Households Income.xlsx"

inflation_rate = 1.029
income_growth_rate = 1.04
df = process_median_income(household_income, inflation_rate, income_growth_rate)
df.head()
# %%
last_year = df["year"].max() - 1
first_year = df["year"].min()
ax = df.plot.line(x="year", y="median_current")
df.plot.line(x="year", y="median_2023", ax=ax)
ax.axvline(2008, color="gray", linestyle="-", alpha=0.25)
ax.axvline(2020, color="gray", linestyle="-", alpha=0.25)
ax.axvline(last_year, color="black", linestyle="-.", alpha=0.5)
ax.set_title(f"Median Income ({first_year} - {last_year})")
plt.show()

ax = df[df["year"] >= 1998].plot.line(x="year", y="median_current")
df[df["year"] >= 1998].plot.line(x="year", y="median_2023", ax=ax)
ax.axvline(2008, color="gray", linestyle="-", alpha=0.25)
ax.axvline(2020, color="gray", linestyle="-", alpha=0.25)
ax.axvline(last_year, color="black", linestyle="-.", alpha=0.5)
ax.set_title(f"Median Income (1998 - {last_year})")
plt.show()
