import os
import datetime as dt
from tqdm import tqdm
import pandas as pd
from typing import Callable
from praw import Reddit
from praw.models import MoreComments
from praw.reddit import Submission

from src.summarize.summarize_tools import submission_sentiment_summarization
from src.text_processing import lower_text_and_remove_all_non_asci

try:
    from ..praw_tools import (
        get_submission_list_by_search,
        get_comments_from_submission,
        get_reddit_client
    )
except:
    from src.praw_tools import (
        get_submission_list_by_search,
        get_comments_from_submission,
        get_reddit_client
    )

try:
    from ..text_processing import (
        lower_text_and_remove_all_non_asci,
        get_tickers_from_string,
        get_ticker_and_name_map
    )
except:
    from src.text_processing import (
        lower_text_and_remove_all_non_asci,
        get_tickers_from_string,
        get_ticker_and_name_map
    )


def get_ticker_finder(path: str):
    """
    desgined for this dataframe. this does not include index tickers.
    https://github.com/JerBouma/FinanceDatabase/blob/main/database/equities.csv
    """
    equities = pd.read_csv(path)
    def rm(x):
        try:
            if "^" in x:
                return "N/A"
            else:
                return x
        except:
            return "N/A"
    where = equities["symbol"].map(rm) != "N/A"
    tickers = equities.loc[where]["symbol"].dropna().map(lambda x: x.lower()).to_list()
    def ticker_finder(sentance: str):
        tickers_found = []
        for word in lower_text_and_remove_all_non_asci(sentance).split():
            if word in tickers:
                tickers_found.append(word)
        return tickers_found
    return ticker_finder


def get_daily_discussion_title(year: int, month: int, day: int):
    date_dt = dt.datetime(year, month, day)
    if date_dt.weekday() < 5:
        titles = [
            dt.datetime.strftime(
                date_dt,
                "Daily Discussion Thread for %B %-d, %Y"
            ),
            dt.datetime.strftime(
                date_dt,
                "Daily Discussion Thread for %B %d, %Y"
            ),
        ]
        return titles
    else:
        if date_dt.day == 5:
            date_dt -= dt.timedelta(days=1) 
        else:
            date_dt -= dt.timedelta(days=2)

        titles = [
            dt.datetime.strftime(
                date_dt,
                "Weekend Discussion Thread for the Weekend of %B %-d, %Y"
            ),
            dt.datetime.strftime(
                date_dt,
                "Weekend Discussion Thread for the Weekend of %B %d, %Y"
            ),
        ]
        return titles


def get_daily_discussion_submission(reddit: Reddit, year: int, 
                                           month: int, day: int) -> Submission:
    titles = get_daily_discussion_title(year, month, day)
    try:
        for title in titles:
            sub = get_submission_list_by_search(
                reddit.subreddit("wallstreetbets"), title, no_of_submissions=1
            )[0]
            if sub.title == title:
                return sub
        raise Exception("Can't find the daily chat")
    except Exception as e:
        raise e


def get_todays_daily_discussion_title():
    date = dt.datetime.now()
    return get_daily_discussion_title(date.year, date.month, date.day)


def get_todays_daily_discussion_submission(reddit: Reddit) -> Submission:
    date = dt.datetime.now()
    return get_daily_discussion_submission(reddit, date.year, date.month, date.day)


if __name__ == "__main__":
    from src.praw_tools import get_reddit_client 
    get_daily_discussion_title(2024, 12, 15)
    reddit = get_reddit_client()
    sub = get_daily_discussion_submission(reddit, 2024, 12, 15)
