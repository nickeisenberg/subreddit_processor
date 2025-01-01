import os
import datetime as dt
from tqdm import tqdm
from typing import Callable, Literal
from praw import Reddit
from praw.reddit import Submission
from pycoingecko import CoinGeckoAPI

from src.praw_tools import (
    get_submission_list_by_search,
    get_reddit_client
)
from src.text_processing import (
    lower_text_and_remove_all_non_asci
)
from src.process.utils import (
    table_sentiment_summariztion,
    get_sentiment_and_comments_from_submission 
)


def get_tickers_from_string(sentence: str, symbol_to_name_map: dict, 
                            name_to_symbol_map: dict) -> list[str]:
    x = []
    for word in lower_text_and_remove_all_non_asci(sentence).split():
        word = word.lower()
        if word in symbol_to_name_map:
            x.append(symbol_to_name_map[word])
        elif word in name_to_symbol_map:
            x.append(name_to_symbol_map[word])
    return list(set(x))


def make_ticker_and_name_map(top: int):
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


def get_crypto_ticker_finder(top: int) -> Callable[[str], list[str]]:
    sts, nts = make_ticker_and_name_map(top)
    def ticker_finder(comment: str):
        return get_tickers_from_string(
            comment, sts, nts
        )
    return ticker_finder


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
            subreddit=reddit.subreddit("cryptocurrency"), 
            search=title, 
            no_of_submissions=1
        )[0]
    except:
        raise Exception(f"Can't find {title}")


def get_todays_crypto_daily_discussion_title():
    date = dt.datetime.now()
    return get_crypto_daily_discussion_title(date.year, date.month, date.day)


def get_todays_crypto_daily_discussion_submission(reddit: Reddit) -> Submission:
    date = dt.datetime.now()
    return get_crypto_daily_discussion_submission(reddit, date.year, date.month, date.day)


def crypto_daily_discussion_summarization(
        reddit: Reddit,
        year: int,
        month: int,
        day: int, 
        comment_preprocesser: Callable[[str], str],
        sentiment_model: Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]],
        ticker_finder: Callable[[str], list[str]],
        add_summary_to_database: bool = False, 
        add_comments_to_database: bool = False, 
        root: str | None = None):

    submission = get_crypto_daily_discussion_submission(
        reddit, year, month, day
    )

    summary, comments =  get_sentiment_and_comments_from_submission(
        submission=submission,
        praw_comment_preprocesser=comment_preprocesser,
        sentiment_model=sentiment_model,
        phrase_finder=ticker_finder,
        add_summary_to_database=add_summary_to_database, 
        add_comments_to_database=add_comments_to_database, 
        root=root
    )
    
    return summary, comments 


def get_unaccounted_for_crypto_daily_dates(root: str, skip_today: bool = True):
    today = dt.datetime.today()
    today = dt.datetime(year=today.year, month=today.month, day=today.day)
    dates_str= sorted(list(set(
        [x.split("_")[0] for x in os.listdir(root)]
    )))
    dates_dt = [dt.datetime.strptime(x, "%Y-%m-%d") for x in dates_str]
    get = []
    check = dates_dt[0]
    while check < today:
        check += dt.timedelta(days=1)
        if check not in dates_dt:
            get.append(check)
    if not skip_today:
        get.append(today)
    return get


def update_crypto_datebase_dailies(root: str, reddit: Reddit,
                                   ticker_finder: Callable[[str], list[str]],
                                   sentiment_model: Callable,
                                   skip_today: bool = True):
    dates_to_look_for = tqdm(get_unaccounted_for_crypto_daily_dates(root, skip_today))
    for i, date in enumerate(dates_to_look_for):
        dates_to_look_for.set_postfix(progress=f"{i + 1} / {len(dates_to_look_for)}")
        try:
            add_crypto_daily_discussion_summary_to_database(
                root=root, reddit=reddit, date=date, phrase_finder=ticker_finder,
                sentiment_model=sentiment_model
            )
        except Exception as e:
            print(e)


if __name__ == "__main__":
    pass
    from src.sentiment_models.models import get_twitter_roberta_base
    from src.text_processing import default_comment_processer
    
    model = get_twitter_roberta_base("cuda")
    reddit = get_reddit_client()
    finder = get_crypto_ticker_finder(100)
    sub = get_todays_crypto_daily_discussion_submission(reddit)
    path = "/home/nicholas/gitrepos/ticker_sentiment/data/crypto/daily_discussions/individual/2019-03-09_ayxcwl.csv"
    sum = table_sentiment_summariztion(path, default_comment_processer(), model, finder)
















