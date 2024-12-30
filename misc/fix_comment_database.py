import os
from tqdm import tqdm
from src.summarize.summarize_tools import Comments

root_dst = "/home/nicholas/gitrepos/ticker_sentiment/data/crypto/daily_discussions/individual/comments"
root_src = "/home/nicholas/gitrepos/ticker_sentiment/data/crypto/daily_discussions/individual/comments_old"
paths = [os.path.join(root_src, x) for x in os.listdir(root_src)]

for path in tqdm(paths):
    with open(path, "r") as f:
        lines = f.readlines()
    
    comments = Comments()
    for i, current_line in enumerate(lines):
        row = comments.new_row
        try:
            row.date, row.submission_id = os.path.basename(path).split(".txt")[0].split("_")
            comment_id, comment = current_line.strip().split(":")
            row.comment_id = comment_id
            row.comment = comment.strip()
        except:
            continue
        comments.add_row(row)

    dst = os.path.join(root_dst, os.path.basename(path).split(".txt")[0] + ".csv")
    comments.table.to_csv(dst)
