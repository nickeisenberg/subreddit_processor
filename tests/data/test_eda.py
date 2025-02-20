import os
import pandas as pd
import src.data.eda as eda

def get_all_for_tests():
    root = os.path.join(
        "/home/nicholas/gitrepos/subreddit_processor",
        'database/crypto/daily_discussions/individual/sentiment_twitter'
    )
    all = eda.make_all_csv(root).dropna()
    return all

all = get_all_for_tests()

def test_plot_sentiment_and_close(ticker:str):
    global all
    eda.plot_sentiment_and_close(all, ticker)

test_plot_sentiment_and_close("eth")
