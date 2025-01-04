import datetime as dt
import pandas as pd
from typing import Callable
from praw import Reddit
from praw.reddit import Submission

from src.sentiment.process import get_sentiment_and_comments_from_submission 
from src.praw_tools import (
    get_submission_list_by_search,
    get_reddit_client
)
from src.text_processing import (
    lower_text_and_remove_all_non_asci,
)
from src.sentiment.models.models import SentimentModel


def get_tickers(path) -> list[str]:
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
    return equities.loc[where]["symbol"].dropna().map(lambda x: x.lower()).to_list()


def get_ticker_finder(path: str):
    """
    desgined for this dataframe. this does not include index tickers.
    https://github.com/JerBouma/FinanceDatabase/blob/main/database/equities.csv
    """
    tickers = get_tickers(path)
    def ticker_finder(sentance: str):
        tickers_found = []
        for word in lower_text_and_remove_all_non_asci(sentance).split():
            if word in tickers:
                tickers_found.append(word)
        return tickers_found
    return ticker_finder


def get_wsb_daily_discussion_title(year: int, month: int, day: int):
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


def get_wsb_daily_discussion_submission(reddit: Reddit, year: int, 
                                           month: int, day: int) -> Submission:
    titles = get_wsb_daily_discussion_title(year, month, day)
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


def get_todays_wsb_daily_discussion_title():
    date = dt.datetime.now()
    return get_wsb_daily_discussion_title(date.year, date.month, date.day)


def get_todays_wsb_daily_discussion_submission(reddit: Reddit) -> Submission:
    date = dt.datetime.now()
    return get_wsb_daily_discussion_submission(reddit, date.year, date.month, date.day)


def wsb_daily_discussion_summarization(
        reddit: Reddit,
        year: int,
        month: int,
        day: int, 
        comment_preprocesser: Callable[[str], str],
        sentiment_model: SentimentModel,
        ticker_finder: Callable[[str], list[str]],
        add_summary_to_database: bool = False, 
        add_comments_to_database: bool = False, 
        root: str | None = None):

    submission = get_wsb_daily_discussion_submission(
        reddit, year, month, day
    )

    summary, comments =  get_sentiment_and_comments_from_submission(
        submission=submission,
        praw_comment_preprocesser=comment_preprocesser,
        sentiment_model=sentiment_model,
        phrase_finder=ticker_finder,
        add_summary_to_database=add_summary_to_database, 
        add_comments_to_database=add_comments_to_database, 
        root=root
    )
    
    return summary, comments 


if __name__ == "__main__":
    pass

    from src.praw_tools import get_reddit_client 
    from src.sentiment_models.models import get_finbert
    from src.text_processing import default_comment_processer

    reddit = get_reddit_client()
    
    path = "/home/nicholas/gitrepos/ticker_sentiment/data/stock_market/ticker_database/american_equities.csv"
    finder = get_ticker_finder(path)
    finbert = get_finbert("cuda")
    
    sum, coms = wsb_daily_discussion_summarization(
        reddit=reddit, 
        year=2024, 
        month=12, 
        day=15,
        comment_preprocesser=default_comment_processer(),
        ticker_finder=finder,
        sentiment_model=finbert,
    )
