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

try:
    from ..text_processing import (
        lower_text_and_remove_all_non_asci,
    )
except:
    from src.text_processing import (
        lower_text_and_remove_all_non_asci,
    )


def submission_sentiment_summarization(submission: Submission,
                                       comment_preprocesser: Callable[[str], str],
                                       sentiment_model: Callable,
                                       ticker_finder: Callable[[str], Iterable[str]],
                                       return_comments: bool = False):
    summarization = pd.DataFrame(
        columns=pd.Series(
            [
                "submission_id", "comment_id", "sentiment", "sentiment_score", 
                "tickers_mentioned"
            ]
        ),
        dtype=object
    )

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

        summarization = pd.concat(
            (
                summarization, 
                pd.DataFrame(
                    data=[[
                        submission_id, comment_id, sentiment_label, 
                        sentiment_score, tickers
                    ]],
                    columns=summarization.columns
                )
            )
        )
    
    if not return_comments:
        return summarization

    else:
        return summarization, comments
