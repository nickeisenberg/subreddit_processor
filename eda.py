import os
import pandas as pd
import matplotlib.pyplot as plt
from src.crypto_daily_summarizer import get_overal_sentiment_from_summarization

summaries = sorted([os.path.join("data", x) for x in os.listdir("./data") if x.endswith(".csv")])

sentiments = []
for summary in summaries:
    sent = get_overal_sentiment_from_summarization(pd.read_csv(summary, index_col=0))
    try:
        pos = sent["positive"]
    except:
        pos = 0
    try:
        neg = sent["negative"]
    except:
        neg = 0
    sentiments.append(pos - neg)

plt.plot(sentiments)
plt.show()
