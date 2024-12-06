import os
import re
import string
import datetime as dt
from praw import Reddit
from praw.reddit import Comment, Submission, Subreddit
from collections.abc import Iterator


class RedditClient:
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent

        self._reddit = Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def get_submissions_by_subreddit_search(self,
                                           subreddit_name: str, 
                                           search: str,
                                           num_submissions: int,
                                           sort: str = "revelance") -> list[Submission]:

        subreddit: Subreddit = self._reddit.subreddit(subreddit_name)
        submissions:Iterator[Submission] = subreddit.search(search, sort=sort)

        return [*submissions][: num_submissions]

    def get_submissions_by_id(self, submission_ids: list[str]) -> list[Submission]:
        return [self._reddit.submission(id) for id in submission_ids]


def remove_all_non_asci(text):
    text = re.sub(f"[{re.escape(string.punctuation)}]", '', text)
    text = re.sub("\n", " ", text)
    text = re.sub(r'[^\x00-\x7F]', '', text)
    text = re.sub(r"\w*emote\w*", "", text)
    text = re.sub(r'\b\w{31,}\b', "", text).strip()
    return text


def lower_text_and_remove_all_non_asci(text):
    return remove_all_non_asci(text.lower().strip())


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


def make_dataset(root: str):
    pass


if __name__ == "__main__":
    pass

x = Reddit(
    client_id=os.environ["PRAW_CLIENT_ID"],
    client_secret=os.environ["PRAW_CLIENT_SECRET"],
    user_agent=os.environ["PRAW_USER_AGENT"]
)

crypto: Subreddit = x.subreddit("cryptocurrency")

submission_list = get_submission_list_by_search(
    crypto, 
    "Daily Crypto Discussion",
)

submission = submission_list[4]

comments = get_comments_from_submission(submission)

try:
    dt.datetime.strptime(
        submission.title.split('Daily Crypto Discussion - ')[1][:-8],
        "%B %d, %Y"
    )
except:
    print("cant do")
