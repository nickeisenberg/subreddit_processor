from typing import Callable, Iterable
import pandas as pd
from praw.models import MoreComments
from praw.reddit import Submission

import src.praw_tools as praw_tools
from src.process.callbacks import (
    Processor, 
    SentimentProcessor, 
    CommentProcessor
)
from src.process.models.models import SentimentModel


def submission_processor(submission: Submission, callbacks: Iterable[Processor]):
    for praw_comment in praw_tools.get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        for callback in callbacks:
            callback(
                comment=praw_comment
            )

    return callbacks


def table_processor(table: pd.DataFrame, callbacks: Iterable[Processor]):
    for _, x in table.iterrows():
        kwargs = {col: x[col] for col in x.index.values}
        for callback in callbacks:
            callback(**kwargs)
    return callbacks


def get_comments_from_submission(
        submission: Submission,
        add_comments_to_database: bool = False, 
        root: str | None = None):

    if add_comments_to_database and not root:
        raise Exception("root must be set")

    comments = CommentProcessor()

    _ = submission_processor(submission, [comments])

    if add_comments_to_database and root is not None:
        comments.comments.write(root)

    return comments.comments


def get_sentiment_and_comments_from_submission(
        submission: Submission,
        praw_comment_preprocesser: Callable[[str], str],
        sentiment_model: SentimentModel,
        phrase_finder: Callable[[str], Iterable[str]],
        add_summary_to_database: bool = False, 
        add_comments_to_database: bool = False, 
        root: str | None = None):

    if (add_comments_to_database or add_summary_to_database) and not root:
        raise Exception("root must be set")
    
    sentiment = SentimentProcessor(
        praw_comment_preprocesser=praw_comment_preprocesser, 
        sentiment_model=sentiment_model,
        phrase_finder=phrase_finder
    )
    comments = CommentProcessor()

    _ = submission_processor(submission, [sentiment, comments])

    if add_comments_to_database and root is not None:
        comments.comments.write(root)

    if add_summary_to_database and root is not None:
        sentiment.sentiment.write(root)

    return sentiment.sentiment, comments.comments


def get_sentiment_from_table(
        table: pd.DataFrame,
        praw_comment_preprocesser: Callable[[str], str],
        sentiment_model: SentimentModel,
        phrase_finder: Callable[[str], Iterable[str]],
        add_summary_to_database: bool = False, 
        root: str | None = None):
    if add_summary_to_database and not root:
        raise Exception("root must be set")
    
    sentiment = SentimentProcessor(
        praw_comment_preprocesser=praw_comment_preprocesser, 
        sentiment_model=sentiment_model,
        phrase_finder=phrase_finder
    )

    _ = table_processor(table, [sentiment])

    if add_summary_to_database and root is not None:
        sentiment.sentiment.write(root)

    return sentiment.sentiment


if __name__ == "__main__": 
    pass
