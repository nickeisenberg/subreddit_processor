import pandas as pd
from src.praw_tools import (
    get_submission_from_id, 
    quick_reddit_client,
    get_comments_from_submission_id
)
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

sub_id = "1479k1x"
sub = get_submission_from_id(quick_reddit_client(), sub_id)
coms = get_comments_from_submission_id(quick_reddit_client(), sub_id)

df_main.shape
df_0.shape
df_1.shape

df_0.to_csv("./t.csv")

def add_additions_to_all_csv(additions: list[pd.DataFrame] | pd.DataFrame, 
                             path_to_all_csv: str):
    if isinstance(additions, pd.DataFrame):
        additions = [additions]
    addition = pd.concat(additions).sort_values(by='date')
    addition.to_csv(path_to_all_csv, mode='a', header=False, index=False)
