from copy import deepcopy
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json
import datetime as dt


def make_date_id_map():
    paths = sorted(
        [os.path.join("data", "individual", x) for x in os.listdir("./data/individual") if x.endswith(".csv")]
    )
    dates = [x.split("-")[0].split("/")[-1] for x in paths]
    ids = [x.split("-")[1].split(".")[0] for x in paths]
    return {d: id for d, id in zip(dates, ids)}


def make_all_csv(save_to="./data/all.csv"):
    paths = sorted(
        [
            os.path.join("data", "individual", x) 
            for x in os.listdir("./data/individual") if x.endswith(".csv")
        ]
    )
    dates = [x.split("-")[0].split("/")[-1] for x in paths]
    ids = [x.split("-")[1].split(".")[0] for x in paths]
    id_date = [[x, y] for x, y in zip(ids, dates)]
    id_date_df = pd.DataFrame(id_date, columns=pd.Series(["submission_id", "date"]))
    dfs = [
        pd.read_csv(path, index_col=0, na_values=[], keep_default_na=False)
        for path in paths
    ]
    df = pd.concat(dfs)

    df_with_dates = pd.merge(
        df, id_date_df, "left", left_on="submission_id", right_on="submission_id"
    )
    if save_to:
        df_with_dates.to_csv(save_to)
    return df_with_dates


def get_all_csv(path="./data/all.csv"):
    if not os.path.isfile(path):
        raise Exception("all_csv not found")
    else:
        return pd.read_csv(path, index_col=0, na_values=[], keep_default_na=False)


def get_date_to_id_map(path="data/date_id_key.json"):
    with open(path, "r") as f:
        return json.load(f)


def combine_dfs_by_date_range(start_date: str, end_date: str):
    with open("data/date_id_key.json", "r") as f:
        date_id_map = json.load(f)
            
    date_id_df = pd.DataFrame(
        [[k, v] for k, v in date_id_map.items()], 
        columns=pd.Series(["date", "submission_id"])
    )

    dfs = []
    current = dt.datetime.strptime(start_date, "%Y_%m_%d")
    before = True
    while before:
        current_date = current.strftime("%Y_%m_%d")
        current_path = f"./data/individual/{current_date}-{date_id_map[current_date]}.csv"
        if os.path.isfile(current_path):
            df = pd.read_csv(
                current_path, index_col=0, na_values=[], keep_default_na=False
            )
            dfs.append(
                pd.merge(df, date_id_df, left_on="submission_id", right_on="submission_id")
            )
        current = current + dt.timedelta(days=1)
        if current > dt.datetime.strptime(end_date, "%Y_%m_%d"):
            before = False

    return pd.concat(dfs).reset_index(drop=True)


def coin(symbol: str):
    def coin_(x):
        sym = symbol
        if sym in x.split():
            return sym
        else:
            return "N/A"
    return coin_


def replace_tickers_mentioned_with_one_ticker(df: pd.DataFrame, ticker: str):
    _df = deepcopy(df)
    _df["tickers_mentioned"] = df["tickers_mentioned"].map(coin(ticker))
    return _df.loc[_df["tickers_mentioned"] != "N/A"]


def get_ticker_counts_by_date(df: pd.DataFrame, ticker: str):
    tick_df: pd.DataFrame = replace_tickers_mentioned_with_one_ticker(df, ticker)
    return tick_df.groupby("date")["tickers_mentioned"].count()


def get_sentiment(df: pd.DataFrame, ticker: str | None = None):
    if ticker:
        df = replace_tickers_mentioned_with_one_ticker(df, ticker)
    y = df.groupby(["date", "sentiment"])["sentiment_score"].mean()
    pos: pd.DataFrame = y.loc[y.index.get_level_values(1) == 'positive'].reset_index().drop("sentiment", axis=1)
    neg: pd.DataFrame = y.loc[y.index.get_level_values(1) == 'negative'].reset_index().drop("sentiment", axis=1)
    comb = pd.merge(
        pos, neg, how="outer", left_on="date", right_on="date",
        suffixes=("_pos", "_neg")
    ).replace(np.nan, 0)
    return comb


def get_sentiment_change_by_date(df: pd.DataFrame, ticker: str | None = None):
    comb = get_sentiment(df, ticker)
    return (comb["sentiment_score_pos"] - comb["sentiment_score_neg"]).values


df = get_all_csv()

eth_counts = get_ticker_counts_by_date(df, "eth")

all_sent = get_sentiment_change_by_date(df)
btc_sent = get_sentiment_change_by_date(df, "btc")


plt.plot(eth_counts.to_numpy())
plt.show()

plt.plot(np.cumsum(all_sent))
plt.show()

plt.plot(np.cumsum(btc_sent))
plt.show()
