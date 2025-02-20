import datetime as dt
from copy import deepcopy
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


def make_all_csv(root: str):
    paths = [os.path.join(root, x) for x in os.listdir(root)]
    dfs = [pd.read_csv(path, index_col=0) for path in paths]
    return pd.concat(dfs).sort_values("date")


def missing_days(root, include_today: bool = False):
    files = os.listdir(root)
    dts = sorted([dt.datetime.strptime(x.split("_")[0], "%Y-%m-%d") for x in files])
    today = dt.datetime.strptime(dt.datetime.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    dates = []
    last = dts[-1]
    while last < today:
        last += dt.timedelta(days=1)
        dates.append(last.strftime("%Y-%m-%d"))
    if include_today:
        return dates
    else:
        return dates[:-1]


def isolate_phrase(phrase: str):
    def _phrase(x: str):
        try:
            if phrase in x.split():
                return phrase
            else:
                return "N/A"
        except:
            return "N/A"
    return _phrase 


def replace_phrases_mentioned_with_one_phrase(df: pd.DataFrame, ticker: str):
    _df = deepcopy(df)
    _df["phrases_mentioned"] = df["phrases_mentioned"].map(isolate_phrase(ticker)) 
    return _df.loc[_df["phrases_mentioned"] != "N/A"]


def get_ticker_counts_from_summarization(summarization: pd.DataFrame):
    x = " ".join(
        summarization["phrases_mentioned"].to_numpy()
    ).replace(",", "").replace("N/A", "").split()
    return pd.Series(x).value_counts().to_dict()


def get_ticker_counts_by_date(df: pd.DataFrame, ticker: str):
    tick_df: pd.DataFrame = replace_phrases_mentioned_with_one_phrase(df, ticker)
    return tick_df.groupby("date")["phrases_mentioned"].count()


def get_pos_neutral_neg_from_daily(df: pd.DataFrame, ticker: str | None = None):
    if ticker:
        df = replace_phrases_mentioned_with_one_phrase(df, ticker)
    return df.groupby("sentiment_label")["sentiment_score"].mean()


def get_pos_neutral_neg_by_date(df: pd.DataFrame, ticker: str | None = None):
    if ticker:
        df = replace_phrases_mentioned_with_one_phrase(df, ticker)
    return df.groupby(["date", "sentiment_label"])["sentiment_score"].mean()


def get_pos_neg_by_date(df: pd.DataFrame, ticker: str | None = None):
    y = get_pos_neutral_neg_by_date(df, ticker)
    pos = y.loc[y.index.get_level_values(1) == 'positive'].reset_index().drop("sentiment_label", axis=1)
    neg = y.loc[y.index.get_level_values(1) == 'negative'].reset_index().drop("sentiment_label", axis=1)
    comb = pd.merge(
        pos, neg, how="outer", left_on="date", right_on="date",
        suffixes=("_pos", "_neg")
    ).replace(np.nan, 0)
    return comb


def get_sentiment_sum_by_date(df: pd.DataFrame, ticker: str | None = None):
    comb = get_pos_neg_by_date(df, ticker)
    x = [comb["date"], (comb["sentiment_score_pos"] - comb["sentiment_score_neg"])]
    return pd.DataFrame(data=x, index=pd.Series(["date", "sentiment_score"])).T


def get_ticker_close(ticker: str, start_date: str, end_date: str):
    """
    date format is '2020-01-01'
    """
    y = yf.download(
        f'{ticker}-USD', start=start_date, end=end_date, interval='1d'
    )
    if y is not None:
        x = y["Close"].reset_index()
        x.columns = ["date", ticker.lower()]
        # x["date"] = x["date"].astype(str).map(lambda x: x.replace("-", "_"))
        x["date"] = x["date"].astype(str)
        return x
    else:
        raise Exception("Ticker not found")


def get_close_and_sentiment_df(df: pd.DataFrame, ticker: str, 
                               sentiment_on_ticker: bool = False,):
    if sentiment_on_ticker:
        sent = get_sentiment_sum_by_date(df, ticker)
    else:
        sent = get_sentiment_sum_by_date(df)
    # start_date = str(sent["date"].min()).replace("_", "-")
    # end_date = str(sent["date"].max()).replace("_", "-")
    start_date = str(sent["date"].min())
    end_date = str(sent["date"].max())
    close = get_ticker_close(ticker, start_date=start_date, end_date=end_date)
    return pd.merge(sent, close, on="date")


def plot_sentiment_and_close(df: pd.DataFrame, ticker: str, 
                             sentiment_on_ticker: bool = False, 
                             plot: bool = True):
    if sentiment_on_ticker:
        combined_sent_and_close = get_close_and_sentiment_df(
            df=df, ticker=ticker, sentiment_on_ticker=sentiment_on_ticker
        )
    else:
        combined_sent_and_close = get_close_and_sentiment_df(
            df=df, ticker=ticker, sentiment_on_ticker=sentiment_on_ticker
        )

    dates = pd.to_datetime(combined_sent_and_close["date"]).to_numpy()
    
    close = combined_sent_and_close[ticker].to_numpy()
    sentiment = np.cumsum(combined_sent_and_close["sentiment_score"].to_numpy())

    # Create the plot
    fig, ax1 = plt.subplots()

    # Plot the closing prices on the primary y-axis
    ax1.plot(dates, close, label=f"{ticker} Close", color="blue")
    ax1.set_ylabel(f"{ticker} Close", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.set_ylim(close.min(), close.max())  # Ensure the axis is explicitly 0 to 1

    # Create a secondary y-axis for sentiment scores
    ax2 = ax1.twinx()
    ax2.plot(dates, sentiment, label="Sentiment Score", color="green")
    ax2.set_ylabel("Sentiment Score", color="green")
    ax2.tick_params(axis="y", labelcolor="green")
    ax2.set_ylim(sentiment.min(), sentiment.max())  # Ensure the axis is explicitly -1 to 1

    # Add legends and title
    fig.suptitle("Sentiment and Close Prices")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    if plot:
        plt.show()
    else:
        return fig
