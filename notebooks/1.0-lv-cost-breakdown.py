# %%
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from housing_cost.process.process_cost_breakdown import (
    CATEGORY,
    IS_TOTAL,
    PERCENT,
    SUBCATEGORY,
    USD_ADJUSTED,
    YEAR,
    process_cost_breakdown,
)

df = process_cost_breakdown()

# %%
sub = df[~df[IS_TOTAL]].reset_index()
sub_means = sub.groupby(SUBCATEGORY)[PERCENT].mean().sort_values(ascending=False)

plt.figure(figsize=(10, 12))  # Making the plot taller with a 10x12 figure size
ax = sns.boxplot(
    data=sub,
    x=PERCENT,
    y=SUBCATEGORY,
    order=sub_means.index.values,
    orient="h",
)
ax.set_xlabel("Percent")
ax.set_ylabel("Subcategory")
ax.set_title("Boxplot of Percent by Subcategory")
plt.show()


# %%
"""
The top seven line items account for 50% of the cost, dominated primarily by framing, foundation, and major system rough-ins.
"""
sub_latest: pd.DataFrame = sub[sub[YEAR] == sub[YEAR].max()]
sub_latest = sub_latest.sort_values(by=PERCENT, ascending=False)
sub_latest["cum_percent"] = sub_latest[PERCENT].cumsum()

ax = sub_latest.plot.barh(x=SUBCATEGORY, y=PERCENT, figsize=(8, 10))
ax.xaxis.set_ticks_position("top")
ax.xaxis.set_label_position("top")
ax.set_xlabel("Percent")
plt.show()

sub_latest = sub_latest.sort_values(by="cum_percent", ascending=False)
ax = sub_latest.plot.barh(x=SUBCATEGORY, y="cum_percent", figsize=(8, 10))
ax.xaxis.set_ticks_position("top")
ax.xaxis.set_label_position("top")
ax.set_xlabel("Cumulative Percent")
ax.axvline(x=50, color="k", linestyle="--")
plt.show()

# %%
"""
Framing fluctuates sporadically, with the highest and lowest percentages in the last two surveys.
Major systems rough-ins have all been monotonically increasing. They also make up a significant portion of the total cost.
Over the past 11 years, their combined contribution has increased by 5.7% points.
"""
pivot = (
    df[(df.index.get_level_values(YEAR) >= 2013) & (~df[IS_TOTAL])]
    .reset_index()
    .pivot(index=[CATEGORY, SUBCATEGORY], columns=YEAR, values=PERCENT)
)
pivot["z"] = pivot.std(axis=1) / pivot.mean(axis=1)
pivot["delta"] = (pivot[2024] - pivot[2013]) / pivot[2013]
pivot["diff"] = pivot[2024] - pivot[2013]
pivot = pivot.sort_values(by="diff", ascending=False, key=lambda s: s.abs())
pivot

# %%
"""
Framing, General Metal and Steel for framing,Painting, Drywall are all trending down. This is especially positive for framing,
which has seen a 10 percentage point drop in cost over the past 2 decades.

?? Is this due to real improvements in cost or are all other costs just increasing at a faster rate?

Building Permit Fees, Water & Sewer Fees Inspections, and Major System Rough-Ins are all trending up.
"""
pivoted = (
    df[~df[IS_TOTAL]]
    .reset_index()
    .pivot(index=YEAR, columns=[CATEGORY, SUBCATEGORY], values=PERCENT)
)
axs: list[plt.Axes] = pivoted.plot.line(subplots=True, figsize=(7, 80), legend=False)  # type: ignore
columns: list[tuple[str, str]] = list(pivoted.columns)  # type: ignore
for ax, (category, subcategory) in zip(axs, columns):
    ax.set_ylim((0, None))  # type: ignore
    ax.set_title(f"{subcategory} - {category}", ha="left", x=0, pad=10)  # type: ignore
plt.subplots_adjust(hspace=0.6)
plt.show()

# %%
"""
In inflation adjusted dollars, Framing is much more stable in dollar terms, suggesting the decrease in
percentage is due to other line items increasing at a faster rate.

Indeed, Excavation is increasing in inflation adjusted dollars, as are Building Permit Fees,
Impact Fee, Water & Sewer Fes, Roofing, all Major Systems Rough-Ins and items like Painting,
and Appliances.

In fact, no significant line item shows a decrease in inflation adjusted dollars. The only
decreases are in minor categories like 'other' which may be due to variations in reporting
year-to-year.
"""
pivoted = (
    df[~df[IS_TOTAL]]
    .reset_index()
    .pivot(index=YEAR, columns=[CATEGORY, SUBCATEGORY], values=USD_ADJUSTED)
)
axs: list[plt.Axes] = pivoted.plot.line(subplots=True, figsize=(7, 80), legend=False)  # type: ignore
columns: list[tuple[str, str]] = list(pivoted.columns)  # type: ignore
for ax, (category, subcategory) in zip(axs, columns):
    ax.set_ylim((0, None))  # type: ignore
    ax.set_title(f"{subcategory} - {category}", ha="left", x=0, pad=10)  # type: ignore
plt.subplots_adjust(hspace=0.6)
plt.show()
