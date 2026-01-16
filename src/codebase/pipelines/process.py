from typing import Callable, Iterable
import pandas as pd
from praw.models import MoreComments
from praw.reddit import Submission

from ..news_sources.reddit.praw_tools import get_comments_from_submission
from ..pipelines.callbacks import Processor, CommentSenitment, CommentSaver
from ..models.models import SentimentModel


def submission_processor(submission: Submission, callbacks: Iterable[Processor]):
    for praw_comment in get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        for callback in callbacks:
            callback(comment=praw_comment)

    return callbacks


def table_processor(table: pd.DataFrame, callbacks: Iterable[Processor]):
    for _, x in table.iterrows():
        kwargs = {col: x[col] for col in x.index.values}
        for callback in callbacks:
            callback(**kwargs)
    return callbacks


def get_sentiment_and_comments_from_submission(
    submission: Submission,
    praw_comment_preprocesser: Callable[[str], str],
    sentiment_model: SentimentModel,
    phrase_finder: Callable[[str], Iterable[str]],
    sentiment_database_root: str | None = None,
    comment_database_root: str | None = None,
):
    sentiment = CommentSenitment(
        praw_comment_preprocesser=praw_comment_preprocesser,
        sentiment_model=sentiment_model,
        phrase_finder=phrase_finder,
    )
    comments = CommentSaver()

    _ = submission_processor(submission, [sentiment, comments])

    if comment_database_root is not None:
        comments.comments.write(comment_database_root)

    if sentiment_database_root is not None:
        sentiment.sentiment.write(sentiment_database_root)

    return sentiment.sentiment, comments.comments


def get_sentiment_from_table(
    table: pd.DataFrame,
    praw_comment_preprocesser: Callable[[str], str],
    sentiment_model: SentimentModel,
    phrase_finder: Callable[[str], Iterable[str]],
    add_summary_to_database: bool = False,
    root: str | None = None,
):
    if add_summary_to_database and not root:
        raise Exception("root must be set")

    sentiment = CommentSenitment(
        praw_comment_preprocesser=praw_comment_preprocesser,
        sentiment_model=sentiment_model,
        phrase_finder=phrase_finder,
    )

    _ = table_processor(table, [sentiment])

    if add_summary_to_database and root is not None:
        sentiment.sentiment.write(root)

    return sentiment.sentiment


if __name__ == "__main__":
    pass
