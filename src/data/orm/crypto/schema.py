from typing import Callable
from tqdm import tqdm
import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.session import Session
from sqlalchemy.engine.base import Engine

from src.data.orm.utils import check_query, check


def get_comments(base) -> DeclarativeMeta:
    class Comments(base):
        __tablename__ = 'comments'
        submission_id = db.Column(db.String, primary_key=True)
        comment_id = db.Column(db.String, primary_key=True)
        date = db.Column(db.String, autoincrement=True)
        comment = db.Column(db.String, nullable=True)
    return Comments


def check_comment(row: object, engine: Engine):
    query = check_query(row, "comments", ["submission_id", "comment_id"])
    return check(query, engine)


def get_sentiment(base) -> DeclarativeMeta:
    class Sentiment(base):
        __tablename__ = 'sentiment'
        submission_id = db.Column(db.String, primary_key=True)
        comment_id = db.Column(db.String, primary_key=True)
        date = db.Column(db.String)
        sentiment_model = db.Column(db.String, primary_key=True)
        sentiment_label = db.Column(db.String)
        sentiment_score = db.Column(db.Float)
        tickers_mentioned = db.Column(db.String, nullable=True)
    return Sentiment


def check_sentiment(row: object, engine: Engine):
    query = check_query(
        row, "sentiment", ["submission_id", "comment_id", "sentiment_model"]
    )
    return check(query, engine)


class DailyDiscussion:
    def __init__(self):
        self._base = None
        self._comments = None
        self._sentiment = None
        self._session = None
        self._engine = None

    def start_session(self, engine='sqlite:///database/crypto/daily_discussions/daily_discussion.db'):
        self._engine = create_engine(engine)
        self._session = sessionmaker(bind=self.engine)()
        _ = self.comments
        _ = self.sentiment
        self.base.metadata.create_all(self.engine)
    
    @property
    def engine(self) -> Engine:
        if not self._engine:
            raise Exception("session is not yet started") 
        return self._engine
    
    @property
    def session(self) -> Session:
        if not self._session:
            raise Exception("session is not yet started") 
        return self._session

    @property
    def base(self) -> DeclarativeMeta:
        if self._base is None:
            self._base = declarative_base()
        return self._base

    @property
    def comments(self):
        if self._comments is None:
            self._comments = get_comments(self.base)
        return self._comments
    
    @property
    def sentiment(self):
        if self._sentiment is None:
            self._sentiment = get_sentiment(self.base)
        return self._sentiment

    def sentiment_row(self, submission_id: str, comment_id: str, date: str,
                      sentiment_model: str, sentiment_label: str, 
                      sentiment_score: float, tickers_mentioned: list[str]):
        return self.sentiment(
            submission_id=submission_id, comment_id=comment_id, date=date,
            sentiment_model=sentiment_model, sentiment_label=sentiment_label, 
            sentiment_score=sentiment_score, tickers_mentioned=tickers_mentioned
        )

    def comments_row(self, submission_id: str, comment_id: str, date:str, comment: str):
        return self.comments(
            submission_id=submission_id, comment_id=comment_id, date=date, comment=comment
        )

    def add_row_to_database(self, row: object):
        try:
            self.session.add(row)
            self.session.commit()
        except Exception as e:
            print(e)
            self.session.rollback()

    def add_rows_to_database(self, rows: list[object], check: Callable[[object, Engine], bool]):
        pbar = tqdm(rows)
        num_successful_rows = 0
        num_fail_rows = 0
        for row in pbar:
            if not check(row, self.engine):
                num_fail_rows += 1
                pbar.set_postfix(fail=num_fail_rows)
            else:
                self.session.add(row)
                num_successful_rows += 1
                pbar.set_postfix(success=num_successful_rows)
        self.session.commit()
        print(f"{num_successful_rows} / {len(rows)} rows were made")


if __name__ == "__main__":
    database = DailyDiscussion()
    database.start_session(
        engine='sqlite:///database/crypto/daily_discussions/daily_discussion.db'
    )

    table_name = ""
    primary_keys = [
        "submission_id", "comment_id",
    ]
    row = get_comments(declarative_base())(
        submission_id="a", comment_id="a", date="a", comment="a"
    )
    check_query(row, "table_name", primary_keys)
