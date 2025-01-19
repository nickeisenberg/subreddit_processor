from collections import defaultdict
from tqdm import tqdm
import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.session import Session
from sqlalchemy.engine.base import Engine

from src.data.orm.utils import check_if_primary_key_exists_in_db


def get_comments(base) -> DeclarativeMeta:
    class Comments(base):
        __tablename__ = 'comments'
        submission_id = db.Column(db.String, primary_key=True)
        comment_id = db.Column(db.String, primary_key=True)
        date = db.Column(db.String, autoincrement=True)
        comment = db.Column(db.String, nullable=True)
    return Comments


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


class DailyDiscussion:
    def __init__(self):
        self._base = None
        self._session = None
        self._engine = None
        self._comments = get_comments(self.base)
        self._sentiment = get_sentiment(self.base)

    def start_session(self, 
                      engine='sqlite:///database/crypto/daily_discussions/daily_discussion.db'):
        self._engine = create_engine(engine)
        self._session = sessionmaker(bind=self.engine)()
        for table in self.tables:
            _ = self.tables[table]
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

    def add_row_to_database(self, row: object):
        try:
            self.session.add(row)
            self.session.commit()
        except Exception as e:
            print(e)
            self.session.rollback()

    def add_rows_to_database(self, rows: list[object]):
        pbar = tqdm(rows)
        session_keys = defaultdict(int)
        num_successful_rows = 0
        num_fail_rows = 0
        print("adding the rows to the session")
        for row in pbar:
            table = row.__getattribute__("__table__")
            table_name = table.name
            row_primary_key_values = {
                x.name: row.__getattribute__(x.name) for x in table.primary_key
            }
            row_primary_key_values_str = table_name + "-" + "-".join(
                [
                    str(row_primary_key_values[key]) for key in row_primary_key_values 
                ]
            )
            if check_if_primary_key_exists_in_db(table_name=table_name, 
                                                 primary_keys=row_primary_key_values, 
                                                 engine=self.engine):
                num_fail_rows += 1
                pbar.set_postfix(success=num_successful_rows, fail=num_fail_rows)
            elif session_keys[row_primary_key_values_str] == 1:
                num_fail_rows += 1
                pbar.set_postfix(success=num_successful_rows, fail=num_fail_rows)
            else:
                self.session.add(row)
                session_keys[row_primary_key_values_str] = 1
                num_successful_rows += 1
                pbar.set_postfix(success=num_successful_rows, fail=num_fail_rows)
        print("committing the session")
        self.session.commit()
        print(f"{num_successful_rows} / {len(rows)} rows were made")

    @property
    def tables(self):
        return {
            "comments": self._comments,
            "sentiment": self._sentiment
        }

    def sentiment_row(self, submission_id: str, comment_id: str, date: str,
                      sentiment_model: str, sentiment_label: str, 
                      sentiment_score: float, tickers_mentioned: list[str]):
        return self.tables["sentiment"](
            submission_id=submission_id, comment_id=comment_id, date=date,
            sentiment_model=sentiment_model, sentiment_label=sentiment_label, 
            sentiment_score=sentiment_score, tickers_mentioned=tickers_mentioned
        )

    def comments_row(self, submission_id: str, comment_id: str, date:str, comment: str):
        return self.tables["comments"](
            submission_id=submission_id, comment_id=comment_id, date=date, comment=comment
        )


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
