import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeMeta

from src.data.orm.base import Database 


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


class DailyDiscussion(Database):
    def __init__(self):
        self._comments = get_comments(self.base)
        self._sentiment = get_sentiment(self.base)

    def start_session(self, 
                      engine='sqlite:///database/crypto/daily_discussions/daily_discussion.db'):
        self.engine = create_engine(engine)
        self.session = sessionmaker(bind=self.engine)()
        for table in self.tables:
            _ = self.tables[table]
        self.base.metadata.create_all(self.engine)
    
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
