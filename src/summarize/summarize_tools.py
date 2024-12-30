import datetime as dt
import pandas as pd
from typing import Callable, Iterable, Literal
from praw.models import MoreComments
from praw.reddit import Submission

from src.praw_tools import (
    get_comments_from_submission,
)
from src.orm import Comments, Sentiment


def get_date_from_submission(submission: Submission):
    return dt.datetime.fromtimestamp(submission.created).strftime("%Y-%m-%d")


def submission_sentiment_summarization(
        submission: Submission,
        praw_comment_preprocesser: Callable[[str], str],
        sentiment_model: Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]],
        ticker_finder: Callable[[str], Iterable[str]]):
    
    summary = Sentiment()
    comments = Comments()

    submission_id = submission.id
    date = get_date_from_submission(submission)

    for praw_comment in get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        summary_row = summary.new_row
        comments_row = comments.new_row

        comments_row.date = date
        comments_row.submission_id = submission_id
        comments_row.comment_id = praw_comment.id
        comments_row.comment = praw_comment.body 
        comments.add_row(comments_row)

        processed_comment = praw_comment_preprocesser(
            praw_comment.body
        )

        if not processed_comment:
            continue

        summary_row.date = date
        summary_row.submission_id = submission_id
        summary_row.comment_id = praw_comment.id
        summary_row.sentiment, summary_row.sentiment_score = sentiment_model(processed_comment)
        summary_row.tickers_mentioned = ticker_finder(processed_comment)
        summary.add_row(summary_row)

    return summary.table, comments.table 


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
