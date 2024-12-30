import datetime as dt
import pandas as pd
from typing import Callable, Iterable, Literal
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


class SentimentRow:
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


class Sentiment:
    def __init__(self):
        self.rows: list[pd.DataFrame] = []
    
    @property
    def new_row(self):
        return SentimentRow()

    def add_row(self, row: SentimentRow):
        self.rows.append(row.row)
    
    @property
    def table(self):
        return pd.concat(self.rows)


class CommentsRow:
    def __init__(self):
        self._row = {}
    
        self._date = None
        self._submission_id = None
        self._comment_id = None
        self._comment = None
    
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
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, comment: str):
        self._row["comment"] = comment
        self._comment = comment


class Comments:
    def __init__(self):
        self.rows: list[pd.DataFrame] = []
    
    @property
    def new_row(self):
        return CommentsRow()

    def add_row(self, row: CommentsRow):
        self.rows.append(row.row)
    
    @property
    def table(self):
        return pd.concat(self.rows)


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
