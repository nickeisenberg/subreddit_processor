from src.crypto_daily_summarizer import (
    crypto_daily_discussion_summarization,
    get_reddit_client,
    get_fin_bert
)
from tqdm import tqdm
import os
import datetime as dt

reddit = get_reddit_client(
    client_id=os.environ["PRAW_CLIENT_ID"],
    client_secret=os.environ["PRAW_CLIENT_SECRET"],
    user_agent=os.environ["PRAW_USER_AGENT"]
)
sentiment_model = get_fin_bert("cuda")

today = dt.datetime.today()

for i in tqdm(range(365 * 6)):
    date = today - dt.timedelta(days=i)
    summarization = crypto_daily_discussion_summarization(
        reddit, date.year, date.month, date.day, 100, sentiment_model
    )
    date_str = dt.datetime.strftime(date, "%Y_%m_%d")
    submission_id = summarization["submission_id"].values[0]
    save_to = f"./data/{date_str}-{submission_id}.csv"
    summarization.to_csv(save_to)
