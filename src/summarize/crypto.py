import os
import datetime as dt
from tqdm import tqdm
import pandas as pd
from typing import Callable, Iterable
from praw import Reddit
from praw.models import MoreComments
from praw.reddit import Submission

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

from src.summarize.summarize_tools import submission_sentiment_summarization


def get_crypto_daily_discussion_title(year: int, month: int, day: int):
    return dt.datetime.strftime(
        dt.datetime(year, month, day),
        "Daily Crypto Discussion - %B %-d, %Y (GMT+0)"
    )


def get_crypto_daily_discussion_submission(reddit: Reddit, year: int, 
                                           month: int, day: int) -> Submission:
    title = get_crypto_daily_discussion_title(year, month, day)
    try:
        return get_submission_list_by_search(
            reddit.subreddit("cryptocurrency"), title, no_of_submissions=1
        )[0]
    except:
        raise Exception("Can't find the daily chat")


def get_todays_crypto_daily_discussion_title():
    date = dt.datetime.now()
    return get_crypto_daily_discussion_title(date.year, date.month, date.day)


def get_todays_crypto_daily_discussion_submission(reddit: Reddit) -> Submission:
    date = dt.datetime.now()
    return get_crypto_daily_discussion_submission(reddit, date.year, date.month, date.day)


def crypto_daily_discussion_summarization(reddit: Reddit,
                                          year: int,
                                          month: int,
                                          day: int, 
                                          num_top_cyptos: int,
                                          sentiment_model: Callable,
                                          return_comments: bool = False):

    submission = get_crypto_daily_discussion_submission(
        reddit, year, month, day
    )

    sts, nts = get_ticker_and_name_map(num_top_cyptos)
    def ticker_finder(comment: str):
        return get_tickers_from_string(
            comment, sts, nts
        )
    
    return submission_sentiment_summarization(
        submission=submission,
        comment_preprocesser=lower_text_and_remove_all_non_asci,
        sentiment_model=sentiment_model,
        ticker_finder=ticker_finder,
        return_comments=return_comments
    )


def crypto_daily_discussion_summarization_old(reddit: Reddit,
                                          year: int,
                                          month: int,
                                          day: int, 
                                          num_top_cyptos: int,
                                          sentiment_model: Callable,
                                          return_comments: bool = False):
    """will delete soon"""
    columns = pd.Series(
        ["submission_id", "comment_id", "sentiment", "sentiment_score", "tickers_mentioned"]
    )
    summarization = pd.DataFrame(
        columns=columns,
        dtype=object
    )

    submission = get_crypto_daily_discussion_submission(
        reddit, year, month, day
    )
    submission_id = submission.id

    comments = []

    sts, nts = get_ticker_and_name_map(num_top_cyptos)
    for praw_comment in get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        comment = lower_text_and_remove_all_non_asci(
            praw_comment.body
        )

        if len(comment) > 512:
            continue

        comment_id = praw_comment.id

        if return_comments:
            comments.append([comment_id, comment])
        
        sentiment = sentiment_model(comment)

        sentiment_label = sentiment[0]["label"]
        sentiment_score = sentiment[0]["score"]

        tickers = get_tickers_from_string(
            comment, sts, nts
        )

        tickers = ", ".join(tickers) if tickers else "N/A"
        
        data = [submission_id, comment_id, sentiment_label, sentiment_score, tickers] 

        comment_summarization = pd.DataFrame(
            data=[data],
            columns=columns
        )


        summarization = pd.concat((summarization, comment_summarization))
    
    if not return_comments:
        return summarization
    else:
        return summarization, comments


def add_crypto_daily_discussion_summary_to_database(
        root: str, reddit: Reddit, date: str | dt.datetime, sentiment_model: Callable,
        overwrite: bool = False):
    
    if isinstance(date, str):
        date = dt.datetime.strptime(date, "%Y-%m-%d")
    date_str = dt.datetime.strftime(date, "%Y-%m-%d")

    try:
        summarization, comments = crypto_daily_discussion_summarization(
            reddit, date.year, date.month, date.day, 100, sentiment_model, True
        )
        submission_id = summarization["submission_id"].values[0]
    except:
        raise Exception("date not found")

    save_csv_to = os.path.join(root, f"{date_str}_{submission_id}.csv")
    save_comments_to = os.path.join(root, f"{date_str}_{submission_id}.txt")
    
    if not overwrite:
        if os.path.isfile(save_csv_to) or os.path.isfile(save_comments_to):
            raise Exception("file already exists")

    summarization.to_csv(save_csv_to)

    with open(save_comments_to, "a") as f:
        for comment in comments:
            comment_id, comment = comment
            _ = f.write(f"{comment_id}: {comment}\n")


def get_unaccounted_for_crypto_daily_dates(root: str, skip_today: bool = True):
    today = dt.datetime.today()
    today = dt.datetime(year=today.year, month=today.month, day=today.day)
    dates_str= sorted(list(set(
        [x.split("_")[0] for x in os.listdir(root)]
    )))
    dates_dt = [dt.datetime.strptime(x, "%Y-%m-%d") for x in dates_str]
    get = []
    check = dates_dt[0]
    while check < today:
        check += dt.timedelta(days=1)
        if check not in dates_dt:
            get.append(check)
    if not skip_today:
        get.append(today)
    return get


def update_crypto_datebase_dailies(root: str, reddit: Reddit, sentiment_model: Callable,
                                   skip_today: bool = True):
    dates_to_look_for = tqdm(get_unaccounted_for_crypto_daily_dates(root, skip_today))
    for i, date in enumerate(dates_to_look_for):
        dates_to_look_for.set_postfix(progress=f"{i + 1} / {len(dates_to_look_for)}")
        try:
            add_crypto_daily_discussion_summary_to_database(
                root, reddit, date, sentiment_model
            )
        except Exception as e:
            print(e)



