from tqdm import tqdm
import datetime as dt

from transformers import logging
logging.set_verbosity_error()

from src.process.models.models import FinBERT
from src.process.process import get_sentiment_and_comments_from_submission 
from src.text_processing import default_comment_processer
from src.subreddits.crypto import (
    get_crypto_ticker_finder, 
    get_crypto_daily_discussion_submission
)
from src.data.eda import missing_days
from src.praw_tools import get_reddit_client


def main():
    sent_root = "/home/nicholas/gitrepos/subreddit_processor/database/crypto/daily_discussions/individual/sentiment_finbert"
    reddit = get_reddit_client()
    
    model = FinBERT(0)
    ticker_finder = get_crypto_ticker_finder(100)
    
    days_to_get = missing_days(sent_root)
    pbar = tqdm(days_to_get)
    for i, day in enumerate(pbar):
        pbar.set_postfix(prog=f"{i + 1} / {len(days_to_get)}")
        day_dt = dt.datetime.strptime(day, "%Y-%m-%d")
        year, month, day = day_dt.year, day_dt.month, day_dt.day
        submission = get_crypto_daily_discussion_submission(reddit, year, month, day)
    
        _ = get_sentiment_and_comments_from_submission(
            submission=submission,
            praw_comment_preprocesser=default_comment_processer(),
            sentiment_model=model,
            phrase_finder=ticker_finder,
            sentiment_database_root=sent_root
        )

# main()
