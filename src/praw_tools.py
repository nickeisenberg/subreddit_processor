import datetime as dt
from typing import Literal
from praw import Reddit
from praw.reddit import Comment, Submission, Subreddit
import os


def get_reddit_client(client_id: str = os.environ["PRAW_CLIENT_ID"],
                      client_secret: str = os.environ["PRAW_CLIENT_SECRET"],
                      user_agent: str = os.environ["PRAW_USER_AGENT"]):
        return Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )


def get_submission_list_from_subreddit(
        subreddit: Subreddit,
        sort_by: Literal['top', 'hot', 'new', 'rising'],
        no_of_submissions: int = 10,
        time_filter: Literal["all", "day", "hour", "month", "week"] = "all"):
    """
    Returns a list of praw Submissions from a praw Subreddit. time_filter is
    only for sort_by='top'.
    """

    if sort_by == 'top':
        submissions = subreddit.top(
            limit=no_of_submissions,
            time_filter=time_filter
        )
    elif sort_by == 'hot':
        submissions = subreddit.hot(limit=no_of_submissions)
    elif sort_by == 'new':
        submissions = subreddit.new(limit=no_of_submissions)
    elif sort_by == 'rising':
        submissions = subreddit.rising(limit=no_of_submissions)

    return list(submissions) 


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


def get_submission_from_id(reddit: Reddit,
                           submission_id: str):
    return reddit.submission(submission_id)


def get_comments_from_submission_id(reddit: Reddit,
                                    submission_id: str,
                                    replace_more_limit=0):
    return  get_comments_from_submission(
        submission=get_submission_from_id(reddit, submission_id),
        replace_more_limit=replace_more_limit
    )


def get_date_from_submission(submission: Submission):
    return dt.datetime.fromtimestamp(submission.created).strftime("%Y-%m-%d")


def get_ymd_date_from_comment(comment: Comment):
    return dt.datetime.fromtimestamp(comment.created).strftime("%Y-%m-%d")


def get_ymd_date_from_submission(submission: Submission):
    return dt.datetime.fromtimestamp(submission.created).strftime("%Y-%m-%d")
