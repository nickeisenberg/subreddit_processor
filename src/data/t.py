import os 
import pandas as pd


root = "/home/nicholas/gitrepos/ticker_sentiment/database/crypto/daily_discussions/individual/sentiment"
paths = [os.path.join(root, x) for x in os.listdir(root)]

dfs = [pd.read_csv(path, index_col=0) for path in paths]
master = pd.concat(dfs).sort_values("date")

master.shape
