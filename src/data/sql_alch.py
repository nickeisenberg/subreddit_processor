from sqlalchemy import create_engine
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self):
        self._base = None
        self._comments = None
        self._sentiment = None
        self._session = None
        self._engine = None

    def start_session(self, engine='sqlite:///example.db'):
        self._engine = create_engine(engine)
        self._session = sessionmaker(bind=self.engine)()
        _ = self.comments
        _ = self.sentiment
        self.base.metadata.create_all(self.engine)
    
    @property
    def engine(self):
        if not self._engine:
            raise Exception("session is not yet started") 
        return self._engine
    
    @property
    def session(self) -> db.orm.Session:
        if not self._session:
            raise Exception("session is not yet started") 
        return self._session

    @property
    def base(self):
        if self._base is None:
            self._base = declarative_base()
        return self._base

    def add_row_to_comments(self, submission_id, comment_id, date, comment):
        row = self.comments(
            submission_id=submission_id, comment_id=comment_id, date=date, comment=comment
        ) 
        self.session.add(row)
        self.session.commit()

    def add_row_to_sentiment(self, submission_id, comment_id, date,
                             sentiment_model, sentiment_label, sentiment_score):
        row = self.sentiment(
            submission_id=submission_id, comment_id=comment_id, date=date,
            sentiment_model=sentiment_model, sentiment_label=sentiment_label, 
            sentiment_score=sentiment_score
        )
        self.session.add(row)
        self.session.commit()

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


def get_comments(base):
    class Comments(base):
        __tablename__ = 'comments'
        submission_id = db.Column(db.String, primary_key=True)
        comment_id = db.Column(db.Integer, primary_key=True)
        date = db.Column(db.String, autoincrement=True)
        comment = db.Column(db.String, nullable=False)
    return Comments


def get_sentiment(base):
    class Sentiment(base):
        __tablename__ = 'sentiment'
        submission_id = db.Column(db.String, nullable=False, primary_key=True)
        comment_id = db.Column(db.Integer, nullable=True, primary_key=True)
        date = db.Column(db.String)
        sentiment_model = db.Column(db.String)
        sentiment_label = db.Column(db.String)
        sentiment_score = db.Column(db.Float)
    return Sentiment

database = Database()
database.start_session()

# # Query the database
# users = session.query(User).all()
# for user in users:
#     print(user.name, user.age, user.email)
