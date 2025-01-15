import datetime as dt
from typing import Callable
from praw import Reddit
from praw.reddit import Submission
from pycoingecko import CoinGeckoAPI

from src.praw_tools import (
    get_submission_list_by_search,
)
from src.process.models.models import SentimentModel
from src.text_processing import (
    lower_text_and_remove_all_non_asci
)
from src.process.process import (
    get_sentiment_and_comments_from_submission 
)


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
        sentiment_model: SentimentModel,
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


if __name__ == "__main__":
    pass
