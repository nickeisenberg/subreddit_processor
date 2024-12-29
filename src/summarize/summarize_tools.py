import datetime as dt
import pandas as pd
from typing import Callable, Iterable, Iterator, Literal
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


class SummaryRow:
    def __init__(self):
        self._row = {}
    
        self._submission_id = None
        self._comment_id = None
        self._date = None
        self._sentiment = None
        self._sentiment_score = None
        self._tickers_mentioned = None
    
    @property
    def row(self):
        return pd.DataFrame(self._row, index=pd.Series([0]))

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date: str):
        self._row["date"] = date
        self._date = date

    @property
    def submission_id(self):
        return self._submission_id

    @submission_id.setter
    def submission_id(self, submission_id: str):
        self._row["submission_id"] = submission_id
        self._submission_id = submission_id

    @property
    def comment_id(self):
        return self._comment_id

    @comment_id.setter
    def comment_id(self, comment_id: str):
        self._row["comment_id"] = comment_id
        self._comment_id = comment_id

    @property
    def sentiment(self):
        return self._sentiment

    @sentiment.setter
    def sentiment(self, sentiment: Literal["positive", "neutral", "negative"]):
        if not sentiment in ["positive", "neutral", "negative"]:
            raise Exception("sentiment must be 'positive', 'neutral' or 'negative'")
        self._row["sentiment"] = sentiment
        self._sentiment = sentiment

    @property
    def sentiment_score(self):
        return self._sentiment_score

    @sentiment_score.setter
    def sentiment_score(self, sentiment_score: float):
        self._row["sentiment_score"] = sentiment_score
        self._sentiment_score = sentiment_score

    @property
    def tickers_mentioned(self):
        return self._tickers_mentioned

    @tickers_mentioned.setter
    def tickers_mentioned(self, tickers: Iterable[str]):
        tickers_str = ", ".join(tickers) if tickers else "N/A"
        self._row["tickers_mentioned"] = tickers_str
        self._tickers_mentioned = tickers_str


class Summary:
    def __init__(self):
        self.rows: list[pd.DataFrame] = []
    
    @property
    def new_row(self):
        return SummaryRow()

    def add_row(self, row: SummaryRow):
        self.rows.append(row.row)
    
    @property
    def summary(self):
        return pd.concat(self.rows)


class Database:
    pass


def get_date_from_submission(submission: Submission):
    return dt.datetime.fromtimestamp(submission.created).strftime("%Y-%m-%d")


def submission_sentiment_summarization(
        submission: Submission,
        praw_comment_preprocesser: Callable[[str], str],
        sentiment_model: Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]],
        ticker_finder: Callable[[str], Iterable[str]],
        return_comments: bool = False):
    
    summary = Summary()

    submission_id = submission.id
    date = get_date_from_submission(submission)

    comments = []
    for praw_comment in get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        row = summary.new_row

        row.date = date
        row.submission_id = submission_id
        row.comment_id = praw_comment.id

        processed_comment = praw_comment_preprocesser(
            praw_comment.body
        )

        if not processed_comment:
            continue

        if return_comments:
            comments.append([row.comment_id, processed_comment])

        row.sentiment, row.sentiment_score = sentiment_model(processed_comment)

        row.tickers_mentioned = ticker_finder(processed_comment)

        summary.add_row(row)

    summarization = summary.summary
    
    if not return_comments:
        return summarization

    else:
        return summarization, comments
