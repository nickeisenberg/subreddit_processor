import os
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

all_twit, all_finbert = get_all_for_tests()

eda.plot_sentiment_and_close(all_twit, "ada", sentiment_on_ticker=True)
