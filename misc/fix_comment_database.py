import os
import pandas as pd
from src.summarize.summarize_tools import Comments

path = "/home/nicholas/gitrepos/ticker_sentiment/data/crypto/daily_discussions/individual/2019-03-09_ayxcwl.txt"

with open(path, "r") as f:
    lines = f.readlines()

comments = Comments()
for current_line in lines:
    row = comments.new_row
    row.date, row.submission_id = os.path.basename(path).split(".txt")[0].split("_")
    comment_id, comment = current_line.strip().split(":")
    row.comment_id = comment_id
    row.comment = comment.strip()
    comments.add_row(row)

def replace_txt_with_csv_for_comments(root):
    pass
