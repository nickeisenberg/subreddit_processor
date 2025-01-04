from abc import abstractmethod
from typing import Callable, Iterable, Literal
from praw.reddit import Comment

from src.data.orm import Comments, Sentiment


class Base:
    @abstractmethod
    def __call__(self, date, submission_id, comment_id, comment):
        pass


class CommentProcessor(Base):
    def __init__(self):
        self.comments = Comments()

    def __call__(self, date, submission_id, comment_id, comment):
        comment_str = comment.body if isinstance(comment, Comment) else comment
        self.comments.add_row(
            self.comments.new_row(
                date=date,
                submission_id=submission_id,
                comment_id=comment_id,
                comment=comment_str
            )
        )


class SentimentProcessor(Base):
    def __init__(self,
                 praw_comment_preprocesser: Callable[[str], str],
                 sentiment_model: Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]],
                 phrase_finder: Callable[[str], Iterable[str]]):

        self.sentiment = Sentiment()
        self.praw_comment_preprocesser = praw_comment_preprocesser
        self.sentiment_model = sentiment_model
        self.phrase_finder = phrase_finder 

    def __call__(self, date, submission_id, comment_id, comment):
        processed_comment = self.praw_comment_preprocesser(comment)
        if processed_comment:
            sentiment_label, sentiment_score = self.sentiment_model(processed_comment)
            self.sentiment.add_row(
                self.sentiment.new_row(
                    submission_id=submission_id,
                    comment_id=comment_id,
                    date=date,
                    sentiment=sentiment_label,
                    sentiment_score=sentiment_score,
                    tickers_mentioned=self.phrase_finder(processed_comment)
                )
            )


if __name__ == "__main__":
    pass






