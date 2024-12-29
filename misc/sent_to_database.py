import os
from src.sentiment_models.models import get_twitter_roberta_base
from src.summarize.crypto import get_crypto_ticker_finder 

sent = get_twitter_roberta_base()
finder = get_crypto_ticker_finder(100)

root = "/home/nicholas/gitrepos/ticker_sentiment/data/crypto/daily_discussions/individual"
txts = sorted([os.path.join(root, x) for x in os.listdir(root) if x.endswith("txt")])

with open(txts[0], "r") as f:
    lines = f.readlines()

for idx in range(len(lines)):
    ind = lines[idx].find(":")
    comment = lines[idx][ind + 1:].strip()
    senti = sent(comment)[0]
    tickers = finder(comment)
    if tickers and senti == "positive":
        print(comment)
        print(senti)
        print(tickers)
