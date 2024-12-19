from src.summarize.eda_tools import (
    get_all_csv,
)

df = get_all_csv(
    "/home/nicholas/gitrepos/ticker_sentiment/data/crypto/daily_discussions/all.csv"
)

x0 = df["submission_id"].value_counts().index.values[-3]
loc_0 = df["submission_id"].values == x0

x1 = df["submission_id"].value_counts().index.values[-1]
loc_1 = df["submission_id"].values == x1

loc_main = (~loc_0) * (~loc_1)

df_main = df.loc[loc_main]
df_0 = df.loc[loc_0]
df_1 = df.loc[loc_1]
