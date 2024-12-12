import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from src.crypto_daily_summarizer import (
    get_overal_sentiment_from_summarization,
    get_ticker_sentiment,
    get_ticker_counts_from_summarization
)

summaries = sorted([os.path.join("data", x) for x in os.listdir("./data") if x.endswith(".csv")])

sentiments = []
for summary in tqdm(summaries):
    summary_df = pd.read_csv(
        summary, index_col=0, na_values=[], keep_default_na=False
    )
    try:
        sent = get_ticker_sentiment(summary_df)
    except:
        continue
    try:
        pos = sent.loc["btc"]["positive"]
    except:
        pos = 0
    try:
        neg = sent.loc["btc"]["negative"]
    except:
        neg = 0
    sentiments.append(pos - neg)

sentiments = np.array(sentiments)
sentiments[np.isnan(sentiments)] = 0

np.mean(sentiments)

plt.plot(sentiments)
plt.show()
