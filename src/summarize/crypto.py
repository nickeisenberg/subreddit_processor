import os
import datetime as dt
from tqdm import tqdm
from typing import Callable
from praw import Reddit
from praw.reddit import Submission
from pycoingecko import CoinGeckoAPI

try:
    from ..praw_tools import (
        get_submission_list_by_search,
        get_comments_from_submission,
        get_reddit_client
    )
except:
    from src.praw_tools import (
        get_submission_list_by_search,
        get_comments_from_submission,
        get_reddit_client
    )

try:
    from ..text_processing import (
        lower_text_and_remove_all_non_asci,
        get_tickers_from_string,
    )
except:
    from src.text_processing import (
        lower_text_and_remove_all_non_asci,
        get_tickers_from_string,
    )

from src.summarize.summarize_tools import (
    submission_sentiment_summarization,
    table_sentiment_summariztion
)

from src.database.database import (
    write_submission_summary_to_csv,
    write_submission_comments_to_txt,
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
        sentiment_model: Callable[[str], tuple[str, float]],
        ticker_finder: Callable[[str], list[str]],
        return_comments: bool = False, 
        add_summary_to_database: bool = False, 
        add_comments_to_database: bool = False, 
        root: str | None = None):

    if add_comments_to_database and not return_comments:
        raise Exception(
            "add_comments_to_database is set to True but return_comments is set to False"
        )

    if (add_comments_to_database or add_summary_to_database) and not root:
        raise Exception("root must be set")

    submission = get_crypto_daily_discussion_submission(
        reddit, year, month, day
    )

    summary_and_comments =  submission_sentiment_summarization(
        submission=submission,
        comment_preprocesser=comment_preprocesser,
        sentiment_model=sentiment_model,
        ticker_finder=ticker_finder,
        return_comments=return_comments
    )

    if add_comments_to_database and root is not None:
        write_submission_comments_to_txt(
            comments=summary_and_comments[1],
            root=root,
            submission_id=int(submission.id),
            date=dt.datetime(year=year, month=month, day=day),
            overwrite=False
        )

    if add_summary_to_database and root is not None:
        write_submission_summary_to_csv(
            summary=summary_and_comments[0],
            root=root,
            overwrite=False
        )
    
    return summary_and_comments 


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
                root=root, reddit=reddit, date=date, ticker_finder=ticker_finder,
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
