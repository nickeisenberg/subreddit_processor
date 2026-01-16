from abc import ABC, abstractmethod
from typing import Callable, Iterable

from praw.reddit import Comment

from ..models.models import SentimentModel
from ..store.csv_orm import Comments, Sentiment
from ..news_sources.reddit.praw_tools import get_ymd_date_from_comment

class Processor(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass


class CommentSaver(Processor):
    def __init__(self):
        self.comments = Comments()

    def __call__(self, comment: Comment, **_):
        self.comments.add_row(
            self.comments.new_row(
                date=get_ymd_date_from_comment(comment),
                submission_id=comment.submission.id,
                comment_id=comment.id,
                comment=comment.body
            )
        )


class CommentSenitment(Processor):
    def __init__(self,
                 praw_comment_preprocesser: Callable[[str], str],
                 sentiment_model: SentimentModel,
                 phrase_finder: Callable[[str], Iterable[str]]):

        self.sentiment = Sentiment()
        self.praw_comment_preprocesser = praw_comment_preprocesser
        self.sentiment_model = sentiment_model
        self.phrase_finder = phrase_finder 

    def __call__(self, comment: Comment | str, **_):
        if isinstance(comment, Comment):
            self._if_praw_comment(comment, **_)
        elif isinstance(comment, str):
            self._if_str_comment(comment, **_)
    
    def _if_praw_comment(self, comment: Comment, **_):
        processed_comment = self.praw_comment_preprocesser(comment.body)
        if processed_comment:
            sentiment_label, sentiment_score = self.sentiment_model(processed_comment)
            self.sentiment.add_row(
                self.sentiment.new_row(
                    submission_id=comment.submission.id,
                    comment_id=comment.id,
                    date=get_ymd_date_from_comment(comment),
                    sentiment_model=self.sentiment_model.name,
                    sentiment_label=sentiment_label,
                    sentiment_score=sentiment_score,
                    phrases_mentioned=self.phrase_finder(processed_comment)
                )
            )

    def _if_str_comment(self, comment: str, **kwargs):
        processed_comment = self.praw_comment_preprocesser(comment)
        if processed_comment:
            sentiment_label, sentiment_score = self.sentiment_model(processed_comment)
            submission_id = kwargs["submission_id"]
            comment_id = kwargs["comment_id"]
            date = kwargs["date"]
            self.sentiment.add_row(
                self.sentiment.new_row(
                    submission_id=submission_id,
                    comment_id=comment_id,
                    date=date,
                    sentiment_model=self.sentiment_model.name,
                    sentiment_label=sentiment_label,
                    sentiment_score=sentiment_score,
                    phrases_mentioned=self.phrase_finder(processed_comment)
                )
            )

if __name__ == "__main__":
    pass
