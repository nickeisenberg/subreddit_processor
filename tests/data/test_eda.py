import os

import src.data.eda as eda


root = os.path.join(
    os.getcwd(),
    'database/crypto/daily_discussions/individual/sentiment_twitter'
)
all = eda.make_all_csv(root).dropna()

eda.plot_sentiment_and_close(all, "algo")
