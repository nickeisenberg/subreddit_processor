import datetime as dt
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


def submission_sentiment_summarization(
        submission: Submission,
        comment_preprocesser: Callable[[str], str],
        sentiment_model: Callable[[str], tuple[str, float]],
        ticker_finder: Callable[[str], Iterable[str]],
        return_comments: bool = False):

    submission_id = submission.id

    date = dt.datetime.fromtimestamp(submission.created).strftime("%Y-%m-%d")

    summarization_columns=pd.Series(
        [
            "date", "submission_id", "comment_id", "sentiment", 
            "sentiment_score", "tickers_mentioned"
        ]
    )

    comments = []
    comment_summarizations = []
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

        sentiment_label, sentiment_score = sentiment_model(comment)

        tickers = ticker_finder(comment)
        tickers = ", ".join(tickers) if tickers else "N/A"

        comment_summarizations.append(
            pd.DataFrame(
                data=[[
                    date, submission_id, comment_id, sentiment_label, 
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



