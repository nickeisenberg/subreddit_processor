import os
import re
import string
import datetime as dt
import pandas as pd
import numpy as np
from typing import Callable
from praw import Reddit
from praw.models import MoreComments
from praw.reddit import Comment, Submission, Subreddit
from pycoingecko import CoinGeckoAPI
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
from transformers import pipeline


def get_fin_bert(device="cpu"):
    model_name = "ProsusAI/finbert"
    return pipeline(
        task="sentiment-analysis", 
        model=AutoModelForSequenceClassification.from_pretrained(model_name).to(device),
        tokenizer=AutoTokenizer.from_pretrained(model_name),
        device=device  # Specify the device for the pipeline
    )


def remove_all_non_asci(text: str):
    text = re.sub(f"[{re.escape(string.punctuation)}]", '', text)
    text = re.sub("\n", " ", text)
    text = re.sub(r'[^\x00-\x7F]', '', text)
    text = re.sub(r"\w*emote\w*", "", text)
    text = re.sub(r'\b\w{31,}\b', "", text).strip()
    return text


def lower_text_and_remove_all_non_asci(text: str):
    return remove_all_non_asci(text.lower().strip())


def get_ticker_and_name_map(top: int):
    sym_to_sym = {}
    name_to_sym = {}
    cg = CoinGeckoAPI()
    cryptos = cg.get_coins_markets(
        vs_currency='usd', order='market_cap_desc', per_page=top, page=1
    )
    for crypto in cryptos:
        sym = crypto["symbol"].lower()
        name = crypto["name"].lower()
        sym_to_sym[sym] = sym
        name_to_sym[name] = sym
    return sym_to_sym, name_to_sym


def get_tickers_from_string(sentence: str, symbol_to_name_map: dict, 
                            name_to_symbol_map: dict) -> list[str]:
    x = []
    for word in lower_text_and_remove_all_non_asci(sentence).split():
        word = word.lower()
        if word in symbol_to_name_map:
            x.append(symbol_to_name_map[word])
        elif word in name_to_symbol_map:
            x.append(name_to_symbol_map[word])

    return x


def get_reddit_client(client_id: str, client_secret: str, 
                      user_agent: str) -> Reddit:
        return Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )


def get_submission_list_from_subreddit(subreddit: Subreddit,
                                       sort_by: str ='top',
                                       search: str | None  = None,
                                       search_sort_by: str = 'relevance',
                                       no_of_submissions: int = 10):
    """
    Returns a list of praw Submissions from a praw Subreddit
    """

    print('starting submission getter')

    if isinstance(search, str):
        submissions = subreddit.search(search, sort=search_sort_by)
    elif sort_by == 'top':
        submissions = subreddit.top(limit=no_of_submissions)
    elif sort_by == 'hot':
        submissions = subreddit.hot(limit=no_of_submissions)
    elif sort_by == 'new':
        submissions = subreddit.new(limit=no_of_submissions)
    elif sort_by == 'rising':
        submissions = subreddit.rising(limit=no_of_submissions)
    else:
        raise Exception("")

    submission_list: list[Submission] = []
    for i, sub in enumerate(submissions):
        submission_list.append(sub)
        if len(submission_list) == no_of_submissions:
            break
    return submission_list


def get_submission_list_by_search(subreddit: Subreddit,
                                  search: str,
                                  search_sort_by: str = 'relevance',
                                  no_of_submissions: int = 10) -> list[Submission]:

    submissions = subreddit.search(search, sort=search_sort_by)

    submission_list: list[Submission] = []
    count = 1
    for sub in submissions:
        submission_list.append(sub)
        if count == no_of_submissions:
            break
        count += 1

    return submission_list


def get_comments_from_submission(submission: Submission,
                                 replace_more_limit=0):
    """
    Retrieve comments from a submission
    """
    _ = submission.comments.replace_more(limit=replace_more_limit)
    comment_list = submission.comments.list()
    return comment_list


def get_comments_from_submission_list(submission_list: list[Submission],
                                      num_comments_per_submission=10):

    submission_coms = {
        submission: [] for submission in submission_list
    }

    for i, submission in enumerate(list(submission_coms.keys())):
        print(f'{i} / {len(submission_list)}: {submission.title}')
        submission_coms[submission] = get_comments_from_submission(
            submission
        )[:num_comments_per_submission]

    return submission_coms


def get_comments_from_submission_id(reddit: Reddit,
                                    submission_id: str,
                                    replace_more_limit=0):
    submission: Submission = reddit.submission(submission_id)
    return  get_comments_from_submission(submission, replace_more_limit)


def get_crypto_daily_discussion_title(year: int, month: int, day: int):
    return dt.datetime.strftime(
        dt.datetime(year, month, day),
        "Daily Crypto Discussion - %B %-d, %Y (GMT+0)"
    )


def get_crypto_daily_discussion_submission(reddit: Reddit, year: int, 
                                           month: int, day: int) -> Submission:
    title = get_crypto_daily_discussion_title(year, month, day)
    try:
        return get_submission_list_by_search(
            reddit.subreddit("cryptocurrency"), title, no_of_submissions=1
        )[0]
    except:
        raise Exception("Can't find the daily chat")


def get_todays_crypto_daily_discussion_title():
    date = dt.datetime.now()
    return get_crypto_daily_discussion_title(date.year, date.month, date.day)


def get_todays_crypto_daily_discussion_submission(reddit: Reddit) -> Submission:
    date = dt.datetime.now()
    return get_crypto_daily_discussion_submission(reddit, date.year, date.month, date.day)


def crypto_daily_discussion_summarization(reddit: Reddit,
                                         year: int,
                                         month: int,
                                         day: int, 
                                         num_top_cyptos: int,
                                         sentiment_model: Callable):
    columns = pd.Series(
        ["submission_id", "comment_id", "sentiment", "sentiment_score", "tickers_mentioned"]
    )
    summarization = pd.DataFrame(
        columns=columns,
        dtype=object
    )

    submission = get_crypto_daily_discussion_submission(
        reddit, year, month, day
    )
    submission_id = submission.id

    sts, nts = get_ticker_and_name_map(num_top_cyptos)
    for praw_comment in get_comments_from_submission(submission):
        if isinstance(praw_comment, MoreComments):
            continue

        comment = lower_text_and_remove_all_non_asci(
            praw_comment.body
        )

        comment_id = praw_comment.id

        sentiment = sentiment_model(comment)
        sentiment_label = sentiment[0]["label"]
        sentiment_score = sentiment[0]["score"]

        tickers = get_tickers_from_string(
            comment, sts, nts
        )

        tickers = ", ".join(tickers) if tickers else "N/A"
        
        data = [submission_id, comment_id, sentiment_label, sentiment_score, tickers] 

        comment_summarization = pd.DataFrame(
            data=[data],
            columns=columns
        )


        summarization = pd.concat((summarization, comment_summarization))

    return summarization


def get_overal_sentiment_from_summarization(summarization: pd.DataFrame):
    return summarization.groupby("sentiment")["sentiment_score"].sum()


def get_ticker_counts_from_summarization(summarization: pd.DataFrame):
    x = " ".join(summarization["tickers_mentioned"].to_numpy()).replace(",", "").replace("N/A", "").split()
    return pd.Series(x).value_counts().to_dict()


def get_tickers_from_summarization(summarization: pd.DataFrame):
    return  list(get_ticker_counts_from_summarization(summarization).keys())


def coin(symbol: str):
    def coin_(x):
        sym = symbol
        if sym in x.split():
            return sym
        else:
            return "N/A"
    return coin_


def get_ticker_sentiment(summarization: pd.DataFrame):
    sents = []
    for ticker in get_tickers_from_summarization(summarization):
        ticker_sentiment = summarization.loc[summarization["tickers_mentioned"].map(coin(ticker)) != "N/A"]
        ticker_sentiment = ticker_sentiment.groupby("sentiment")["sentiment_score"].sum()
        ticker_sentiment = pd.DataFrame(ticker_sentiment).T.rename_axis("", axis=1)
        ticker_sentiment.index = pd.Series([ticker])
        sents.append(ticker_sentiment)
    return pd.concat(sents)


if __name__ == "__main__":
    pass

reddit = get_reddit_client(
    client_id=os.environ["PRAW_CLIENT_ID"],
    client_secret=os.environ["PRAW_CLIENT_SECRET"],
    user_agent=os.environ["PRAW_USER_AGENT"]
)

sentiment_model = get_fin_bert("cuda")

summarization = crypto_daily_discussion_summarization(
    reddit, 2024, 12, 11, 100, sentiment_model
)

get_overal_sentiment_from_summarization(summarization)
get_ticker_counts_from_summarization(summarization)
get_ticker_sentiment(summarization)
