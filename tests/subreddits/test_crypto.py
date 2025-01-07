import datetime as dt
from src.praw_tools import (
    get_reddit_client,
    get_comments_from_submission
)
from src.subreddits.crypto import get_todays_crypto_daily_discussion_submission


submission = get_todays_crypto_daily_discussion_submission(get_reddit_client())

comments = get_comments_from_submission(submission)

