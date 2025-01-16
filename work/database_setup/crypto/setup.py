from src.data.orm.crypto.schema import DailyDiscussion
from tqdm import tqdm
import pandas as pd
import os

database = DailyDiscussion()
database.start_session(
    engine='sqlite:///database/crypto/daily_discussions/daily_discussion.db'
)

def setup_comments():
    root = "/home/nicholas/gitrepos/subreddit_processor/database/crypto/daily_discussions/individual/comments"
    paths = [os.path.join(root, x) for x in os.listdir(root)]
    comments_dfs = [pd.read_csv(path, index_col=0) for path in paths]
    comments_df = pd.concat(comments_dfs)
    
    for _, row in tqdm(comments_df.iterrows()):
        database.add_row_to_comments(
            submission_id=row["submission_id"], 
            comment_id=row["comment_id"], 
            date=row["date"], 
            comment=row["comment"]
        )

def setup_twit():
    root = "/home/nicholas/gitrepos/subreddit_processor/database/crypto/daily_discussions/individual/sentiment_twitter"
    paths = [os.path.join(root, x) for x in os.listdir(root)]
    twit_sentiment_dfs = [pd.read_csv(path, index_col=0) for path in paths]
    twit_sentiment_df = pd.concat(twit_sentiment_dfs)
    
    exceptions = []
    for idx, row in tqdm(twit_sentiment_df.iterrows()):
        try:
            database.add_row_to_sentiment(
                submission_id=row["submission_id"],
                comment_id=row["comment_id"],
                date=row["date"],
                sentiment_model=row["sentiment_model"],
                sentiment_score=row["sentiment_score"],
                sentiment_label=row["sentiment_label"],
                tickers_mentioned=row["phrases_mentioned"]
            )
        except Exception as e:
            exceptions.append(idx)


def setup_finbert():
    root = "/home/nicholas/gitrepos/subreddit_processor/database/crypto/daily_discussions/individual/sentiment_finbert"
    paths = [os.path.join(root, x) for x in os.listdir(root)]
    finbert_sentiment_dfs = [pd.read_csv(path, index_col=0) for path in paths]
    finbert_sentiment_df = pd.concat(finbert_sentiment_dfs)
    
    exceptions = []
    for idx, row in tqdm(finbert_sentiment_df.iterrows()):
        try:
            database.add_row_to_sentiment(
                submission_id=row["submission_id"],
                comment_id=row["comment_id"],
                date=row["date"],
                sentiment_model=row["sentiment_model"],
                sentiment_score=row["sentiment_score"],
                sentiment_label=row["sentiment_label"],
                tickers_mentioned=row["phrases_mentioned"]
            )
        except Exception as e:
            exceptions.append(idx)


# setup_finbert()
# setup_twit()

result = pd.read_sql(
    "select * from sentiment", 
    database.engine
)

result["sentiment_model"].value_counts()
