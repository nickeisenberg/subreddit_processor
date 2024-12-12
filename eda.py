import os
from typing import Literal
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from src.crypto_daily_summarizer import (
    get_overal_sentiment_from_summarization,
    get_ticker_sentiment,
    get_ticker_counts_from_summarization
)

from sklearn.preprocessing import MinMaxScaler



def get_sentiment_for_ticker(ticker, 
                             which: Literal["positive", "negative"] = "positive", 
                             path="./data"):
    sentiments = []
    summaries = sorted(
        [os.path.join(path, x) for x in os.listdir(path) if x.endswith(".csv")]
    )
    for summary in tqdm(summaries):
        summary_df = pd.read_csv(
            summary, index_col=0, na_values=[], keep_default_na=False
        )
        try:
            sent = get_ticker_sentiment(summary_df)
        except:
            continue
        try:
            pos = sent.loc[ticker][which]
        except:
            pos = 0
        sentiments.append(pos)

    sentiments = np.array(sentiments)

    sentiments[np.isnan(sentiments)] = 0

    return sentiments

btc_pos = get_sentiment_for_ticker("btc")


plt.plot(
    MinMaxScaler().fit_transform(btc_pos.reshape((-1, 1))).reshape(-1)
)
plt.show()
