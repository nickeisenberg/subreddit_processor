import pandas as pd
from typing import Iterable, Literal


class SentimentRow:
    def __init__(self):
        self._submission_id = None
        self._comment_id = None
        self._date = None
        self._sentiment = None
        self._sentiment_score = None
        self._tickers_mentioned = None

    
    @property
    def row(self):
        return pd.DataFrame(self.row_dict, index=pd.Series([0]))
    
    @property
    def row_dict(self):
        return {
            "submission_id": self.submission_id,
            "comment_id": self.comment_id,
            "date": self.date,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "tickers_mentioned": self.tickers_mentioned 
        }

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date: str):
        self._date = date

    @property
    def submission_id(self):
        return self._submission_id

    @submission_id.setter
    def submission_id(self, submission_id: str):
        self._submission_id = submission_id

    @property
    def comment_id(self):
        return self._comment_id

    @comment_id.setter
    def comment_id(self, comment_id: str):
        self._comment_id = comment_id

    @property
    def sentiment(self):
        return self._sentiment

    @sentiment.setter
    def sentiment(self, sentiment: Literal["positive", "neutral", "negative"]):
        if not sentiment in ["positive", "neutral", "negative"]:
            raise Exception("sentiment must be 'positive', 'neutral' or 'negative'")
        self._sentiment = sentiment

    @property
    def sentiment_score(self):
        return self._sentiment_score

    @sentiment_score.setter
    def sentiment_score(self, sentiment_score: float):
        self._sentiment_score = sentiment_score

    @property
    def tickers_mentioned(self):
        return self._tickers_mentioned

    @tickers_mentioned.setter
    def tickers_mentioned(self, tickers: Iterable[str]):
        tickers_str = ", ".join(tickers) if tickers else "N/A"
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
        return pd.concat(self.rows).reset_index(drop=True)


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
        return pd.concat(self.rows).reset_index(drop=True)
