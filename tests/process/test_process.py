import os
import pandas as pd

from transformers import logging
logging.set_verbosity_error()

from src.process.models.models import TwitterRobertaBase 
from src.process.process import get_sentiment_from_table 
from src.text_processing import default_comment_processer
from src.subreddits.crypto import get_crypto_ticker_finder

def test_get_sentiment_from_table():
    root = "/home/nicholas/gitrepos/ticker_sentiment/database/crypto/daily_discussions/individual/comments"
    tables = [pd.read_csv(os.path.join(root, path), index_col=0).dropna() for path in os.listdir(root)]
    model = TwitterRobertaBase("cuda")
    finder = get_crypto_ticker_finder(100)
    
    return get_sentiment_from_table(
        table=tables[0],
        praw_comment_preprocesser=default_comment_processer(),
        sentiment_model=model,
        phrase_finder=finder,
        add_summary_to_database=True,
        root="/home/nicholas/gitrepos/ticker_sentiment/tests/sentiment/"
    )

sent = test_get_sentiment_from_table()
