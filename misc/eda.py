from src.summarize.eda_tools import (
    get_all_csv, 
    plot_sentiment_and_close,
    get_pos_neg_by_date
)

import matplotlib.pyplot as plt

df = get_all_csv()
pos_neg = get_pos_neg_by_date(df, "ada")
noise = (pos_neg["sentiment_score_pos"] - pos_neg["sentiment_score_neg"]).values

ticker = "ada"
plot_sentiment_and_close(df, ticker)
