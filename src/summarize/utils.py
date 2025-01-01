import datetime as dt
import pandas as pd
from typing import Callable, Iterable, Literal
from praw.models import MoreComments
from praw.reddit import Submission

from src.praw_tools import get_date_from_submission
from src.praw_tools import (
    get_comments_from_submission,
)
from src.orm import Comments, Sentiment
from src.summarize.callbacks import (
    Base, 
    SentimentProcessor, 
    CommentProcessor
)


def submission_processor(submission: Submission, callbacks: Iterable[Base]):
    submission_id = submission.id
    date = get_date_from_submission(submission)

    for praw_comment in get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        for callback in callbacks:
            callback(
                date=date,
                submission_id=submission_id,
                comment_id=praw_comment.id,
                comment=praw_comment
            )

    return callbacks


def get_sentiment_and_comments_from_submission(
        submission: Submission,
        praw_comment_preprocesser: Callable[[str], str],
        sentiment_model: Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]],
        ticker_finder: Callable[[str], Iterable[str]]):
    
    sentiment = Sentiment()
    comments = Comments()

    submission_id = submission.id
    date = get_date_from_submission(submission)

    for praw_comment in get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        comments.add_row(
            comments.new_row(
                date=date,
                submission_id=submission_id,
                comment_id=praw_comment.id,
                comment=praw_comment.body 
            )
        )

        processed_comment = praw_comment_preprocesser(
            praw_comment.body
        )

        if not processed_comment:
            continue

        sentiment_label, sentiment_score = sentiment_model(processed_comment)
        sentiment.add_row(
            sentiment.new_row(
                submission_id=submission_id,
                comment_id=praw_comment.id,
                date=date,
                sentiment=sentiment_label,
                sentiment_score=sentiment_score,
                tickers_mentioned=ticker_finder(processed_comment)
            )
        )

    return sentiment, comments


def table_sentiment_summariztion(
        table: str | pd.DataFrame,
        praw_comment_preprocesser: Callable[[str], str],
        sentiment_model: Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]],
        ticker_finder: Callable[[str], Iterable[str]]):

    if isinstance(table, str):
        table = pd.read_csv(table, index_col=0)

    table["comment"] = table["comment"].map(praw_comment_preprocesser).map(lambda x: None if x == "" else x)
    table = table.dropna()
    table[["sentiment", "sentiment_score"]] = table["comment"].map(sentiment_model).apply(pd.Series)
    table["tickers_mentioned"] = table["comment"].map(ticker_finder)
    return table.drop(columns="comment")


def submission_sentiment_summarization_writer(
        submission: Submission,
        comment_preprocesser: Callable[[str], str],
        sentiment_model: Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]],
        ticker_finder: Callable[[str], list[str]],
        add_summary_to_database: bool = False, 
        add_comments_to_database: bool = False, 
        root: str | None = None):

    if (add_comments_to_database or add_summary_to_database) and not root:
        raise Exception("root must be set")

    summary, comments =  get_sentiment_and_comments_from_submission(
        submission=submission,
        praw_comment_preprocesser=comment_preprocesser,
        sentiment_model=sentiment_model,
        ticker_finder=ticker_finder,
    )

    if add_comments_to_database and root is not None:
        comments.write(root)

    if add_summary_to_database and root is not None:
        summary.write(root)
    
    return summary, comments 


if __name__ == "__main__": 
    from src.sentiment_models.models import get_twitter_roberta_base
    from src.text_processing import default_comment_processer
    
    model = get_twitter_roberta_base()
    
    def finder(string: str):
        ticks = ["gme", "amzn"]
        return_ticks = []
        for word in string.split(" "):
            if word in ticks:
                return_ticks.append(word)
        return ", ".join(list(set(return_ticks)))
    
    x = pd.DataFrame(
        {
            "com_ids": [
                "qe43", 
                "asdf", 
                "34532"
            ], 
            "comment": [
                "GME is the first and amzn sucks", 
                "hello there", 
                "this is shitty"
            ], 
        }
    )
    
    table_sentiment_summariztion(x, default_comment_processer(512), model, finder)
