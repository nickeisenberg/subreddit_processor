from sqlalchemy import create_engine
import os
import pandas as pd
import src.data.eda as eda


def get_all_for_tests():
    root = os.path.join(
        "/home/nicholas/gitrepos/subreddit_processor",
        'database/crypto/daily_discussions/individual/sentiment_twitter'
    )
    all_twit = eda.make_all_csv(root).dropna()
    root = os.path.join(
        "/home/nicholas/gitrepos/subreddit_processor",
        'database/crypto/daily_discussions/individual/sentiment_finbert'
    )
    all_finbert = eda.make_all_csv(root).dropna()
    return all_twit, all_finbert

all_twit = pd.read_sql(
    sql="select * from sentiment where sentiment_model = 'twitter_roberta_base'", 
    con=create_engine('sqlite:///database/crypto/daily_discussions/daily_discussion.db')
).rename({"tickers_mentioned": "phrases_mentioned"}, axis=1)

all_finbert = pd.read_sql(
    sql="select * from sentiment where sentiment_model = 'finbert'", 
    con=create_engine('sqlite:///database/crypto/daily_discussions/daily_discussion.db')
).rename({"tickers_mentioned": "phrases_mentioned"}, axis=1)

eda.plot_sentiment_and_close(all_twit, "btc", sentiment_on_ticker=True)

eda.plot_sentiment_and_close(all_finbert, "btc", sentiment_on_ticker=True)
