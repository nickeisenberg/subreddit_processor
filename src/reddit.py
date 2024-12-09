import os
import re
import string
import datetime as dt
from praw import Reddit
from praw.reddit import Comment, Submission, Subreddit
from pycoingecko import CoinGeckoAPI


def remove_all_non_asci(text):
    text = re.sub(f"[{re.escape(string.punctuation)}]", '', text)
    text = re.sub("\n", " ", text)
    text = re.sub(r'[^\x00-\x7F]', '', text)
    text = re.sub(r"\w*emote\w*", "", text)
    text = re.sub(r'\b\w{31,}\b', "", text).strip()
    return text


def lower_text_and_remove_all_non_asci(text):
    return remove_all_non_asci(text.lower().strip())


def get_ticker_and_name_map(top: int):
    sym_to_name = {}
    name_to_sym = {}

    cg = CoinGeckoAPI()
    
    # Fetch the top 100 coins by market capitalization
    cryptos = cg.get_coins_markets(
        vs_currency='usd', order='market_cap_desc', per_page=top, page=1
    )

    for crypto in cryptos:
        sym = crypto["symbol"].lower()
        name = crypto["name"].lower()
        sym_to_name[sym] = sym
        name_to_sym[name] = sym
    return sym_to_name, name_to_sym


def extract_valid_tickers(sentence, symbol_to_name_map: dict, 
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
    count = 1
    for sub in submissions:
        submission_list.append(sub)
        if count == no_of_submissions:
            break
        count += 1

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
    comment_list: list[Comment] = submission.comments.list()
    return comment_list


def get_comments_from_submission_list(submission_list: list[Submission],
                                      num_comments_per_submission=10):

    submission_coms: dict[Submission, list[Comment]] = {
        submission: [] for submission in submission_list
    }

    for i, submission in enumerate(list(submission_coms.keys())):
        print(f'{i} / {len(submission_list)}: {submission.title}')
        submission_coms[submission] = get_comments_from_submission(
            submission
        )[:num_comments_per_submission]

    return submission_coms


def get_comments_from_submission_id(reddit: Reddit,
                                    submission_id: list[str],
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


if __name__ == "__main__":
    pass


reddit = get_reddit_client(
    client_id=os.environ["PRAW_CLIENT_ID"],
    client_secret=os.environ["PRAW_CLIENT_SECRET"],
    user_agent=os.environ["PRAW_USER_AGENT"]
)

counts = {}
today = dt.datetime.now()
for idx in range(10):
    print(idx)
    date = today - dt.timedelta(days=idx)
    submission = get_crypto_daily_discussion_submission(reddit, date.year, date.month, date.day)
    comments = get_comments_from_submission(submission)
    stn, nts = get_ticker_and_name_map(100)
    for idx in range(len(comments)):
        tickers = extract_valid_tickers(
            lower_text_and_remove_all_non_asci(
                comments[idx].body
            ), stn, nts
        )
        for ticker in tickers:
            if ticker in counts:
                counts[ticker] += 1
            else:
                counts[ticker] = 1
counts
