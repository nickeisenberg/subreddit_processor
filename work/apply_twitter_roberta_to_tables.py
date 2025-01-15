import os
import pandas as pd
from tqdm import tqdm

from transformers import logging
logging.set_verbosity_error()

from src.process.models.models import TwitterRobertaBase 
from src.process.process import get_sentiment_from_table 
from src.text_processing import default_comment_processer
from src.subreddits.crypto import get_crypto_ticker_finder

def main():
    root = "/home/nicholas/gitrepos/subreddit_processor/database/crypto/daily_discussions/individual/comments"
    tables = [pd.read_csv(os.path.join(root, path), index_col=0).dropna() for path in os.listdir(root)]
    model = TwitterRobertaBase("cuda")
    finder = get_crypto_ticker_finder(100)
    root = os.path.join(
        "/home/nicholas/gitrepos/subreddit_processor",
        "database/crypto/daily_discussions/individual/sentiment_twitter"
    )
    for table in tqdm(tables):
        _ = get_sentiment_from_table(
            table=table,
            praw_comment_preprocesser=default_comment_processer(),
            sentiment_model=model,
            phrase_finder=finder,
            add_summary_to_database=True,
            root=root
        )

# main()
