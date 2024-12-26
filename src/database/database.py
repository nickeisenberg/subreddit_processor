import os
import pandas as pd
import datetime as dt


def get_submission_id_and_date_from_summary(summary: pd.DataFrame):
    columns = summary.columns
    if not "submission_id" in columns and not "date" in columns:
        raise Exception("submission_id and date are not in the columns of summary")
    submission_id = summary["submission_id"].values[0]
    date_str = summary["date"].values[0]
    return submission_id, date_str


def write_submission_summary_to_csv(summary: pd.DataFrame, root:str,
                                    overwrite: bool = False):

    submission_id, date_str = get_submission_id_and_date_from_summary(summary)

    save_csv_to = os.path.join(root, f"{date_str}_{submission_id}.csv")

    if not overwrite and os.path.isfile(save_csv_to):
        raise Exception(f"{save_csv_to} exists")

    summary.to_csv(save_csv_to)


def write_submission_comments_to_txt(comments: list[str], root:str,
                                     submission_id: int,
                                     date: str | dt.datetime,
                                     overwrite: bool = False):
    if isinstance(date, str):
        date = dt.datetime.strptime(date, "%Y-%m-%d")
    date_str = dt.datetime.strftime(date, "%Y-%m-%d")

    save_comments_to = os.path.join(root, f"{date_str}_{submission_id}.txt")
    
    if not overwrite and os.path.isfile(save_comments_to):
        raise Exception(f"{save_comments_to} exists")

    with open(save_comments_to, "a") as f:
        for comment in comments:
            comment_id, comment = comment
            _ = f.write(f"{comment_id}: {comment}\n")


def write_submission_summary_and_comments_to_database(root: str,
                                                      summary: pd.DataFrame,
                                                      comments: list[str],
                                                      overwrite: bool = False):
    submission_id, date_str = get_submission_id_and_date_from_summary(summary)
    write_submission_summary_to_csv(
        summary=summary, root=root, overwrite=overwrite
    )
    write_submission_comments_to_txt(
        comments=comments, root=root, submission_id=submission_id,
        date=date_str, overwrite=overwrite
    )
