from src.summarize.eda_tools import (
    get_all_csv, 
    plot_sentiment_and_close,
)

from src.praw_tools import get_comments_from_submission_id, get_reddit_client

import os

submission_id = "ayxcwl"
reddit = get_reddit_client(
    client_id=os.environ["PRAW_CLIENT_ID"],
    client_secret=os.environ["PRAW_CLIENT_SECRET"],
    user_agent=os.environ["PRAW_USER_AGENT"]
)
comments = get_comments_from_submission_id(reddit, submission_id)

for com in comments:
    if com.id == "ei67smm":
        print(com.body)

df = get_all_csv()
ticker = "ada"
plot_sentiment_and_close(df, ticker)
