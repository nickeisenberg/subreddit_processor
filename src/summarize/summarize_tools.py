import datetime as dt
import os
import pandas as pd
from typing import Callable, Iterable
from praw.models import MoreComments
from praw.reddit import Submission

try:
    from ..praw_tools import (
        get_comments_from_submission,
    )
except:
    from src.praw_tools import (
        get_comments_from_submission,
    )


def submission_sentiment_summarization(submission: Submission,
                                       comment_preprocesser: Callable[[str], str],
                                       sentiment_model: Callable,
                                       ticker_finder: Callable[[str], Iterable[str]],
                                       return_comments: bool = False):
    summarization_columns=pd.Series(
        [
            "submission_id", "comment_id", "sentiment", "sentiment_score", 
            "tickers_mentioned"
        ]
    )

    comment_summarizations = []

    submission_id = submission.id

    comments = []

    for praw_comment in get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        comment_id = praw_comment.id

        comment = comment_preprocesser(
            praw_comment.body
        )

        if len(comment) > 512:
            continue

        if return_comments:
            comments.append([comment_id, comment])
        
        sentiment = sentiment_model(comment)
        sentiment_label = sentiment[0]["label"]
        sentiment_score = sentiment[0]["score"]

        tickers = ticker_finder(comment)
        tickers = ", ".join(tickers) if tickers else "N/A"

        comment_summarizations.append(
            pd.DataFrame(
                data=[[
                    submission_id, comment_id, sentiment_label, 
                    sentiment_score, tickers
                ]],
                columns=summarization_columns
            )
        )

    summarization = pd.concat(comment_summarizations)
    
    if not return_comments:
        return summarization

    else:
        return summarization, comments


def write_submission_summary_to_csv(summary: pd.DataFrame, root:str,
                                    submission_id: int,
                                    date: str | dt.datetime,
                                    overwrite: bool = False):
    if isinstance(date, str):
        date = dt.datetime.strptime(date, "%Y-%m-%d")
    date_str = dt.datetime.strftime(date, "%Y-%m-%d")

    save_csv_to = os.path.join(root, f"{date_str}_{submission_id}.csv")

    if not overwrite and os.path.isfile(save_csv_to):
        raise Exception(f"{save_csv_to} exists")

    summary.to_csv(save_csv_to)


def write_submission_comments_to_txt(comments: list[str], root:str,
                                     submission_id: int,
                                     date: str | dt.datetime,
                                     overwrite: bool = False):
    if isinstance(date, str):
        date = dt.datetime.strptime(date, "%Y-%m-%d")
    date_str = dt.datetime.strftime(date, "%Y-%m-%d")

    save_comments_to = os.path.join(root, f"{date_str}_{submission_id}.txt")
    
    if not overwrite and os.path.isfile(save_comments_to):
        raise Exception(f"{save_comments_to} exists")

    with open(save_comments_to, "a") as f:
        for comment in comments:
            comment_id, comment = comment
            _ = f.write(f"{comment_id}: {comment}\n")
