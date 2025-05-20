# %%


import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from housing_cost.config import INTERIM_DATA_DIR
from housing_cost.process.process_cost_history import process_cost_history

pd.set_option("display.width", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", None)

part_1_path = INTERIM_DATA_DIR / "NABH Construction Cost - 2024__table_5__values.csv"
part_2_path = INTERIM_DATA_DIR / "NABH Construction Cost - 2024__table_6__values.csv"

df_1, dfc_1 = process_cost_history(part_1_path)
df_2, dfc_2 = process_cost_history(part_2_path)

df = pd.concat([df_1, df_2])
dfc = pd.concat([dfc_1, dfc_2])
df.sort_index()
# %%
# The lions share of the growth in housing costs is due to cost of construction.
sns.lineplot(x="year", y="usd_adjusted", hue="category", data=dfc)
plt.show()
