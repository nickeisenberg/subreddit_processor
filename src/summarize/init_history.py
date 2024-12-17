from .crypto import crypto_daily_discussion_summarization
from ..praw_tools import get_reddit_client
from ..sentiment_models import get_fin_bert
from tqdm import tqdm
import os
import datetime as dt


def init_past():
    """
    get the past 6 years of crypto daily chats
    """
    reddit = get_reddit_client(
        client_id=os.environ["PRAW_CLIENT_ID"],
        client_secret=os.environ["PRAW_CLIENT_SECRET"],
        user_agent=os.environ["PRAW_USER_AGENT"]
    )
    sentiment_model = get_fin_bert("cuda")
    
    start = dt.datetime(2024, 9, 14)
    
    for i in tqdm(range(365 * 6)):
        date = start - dt.timedelta(days=i)
        try:
            summarization, comments = crypto_daily_discussion_summarization(
                reddit, date.year, date.month, date.day, 100, sentiment_model, True
            )
        except:
            print("date not found")
            continue
        date_str = dt.datetime.strftime(date, "%Y_%m_%d")
        submission_id = summarization["submission_id"].values[0]
        save_csv_to = f"./data/{date_str}-{submission_id}.csv"
        summarization.to_csv(save_csv_to)
        save_comments_to = f"./data/{date_str}-{submission_id}.txt"
        with open(save_comments_to, "a") as f:
            for comment in comments:
                comment_id, comment = comment
                _ = f.write(f"{comment_id}: {comment}\n")

