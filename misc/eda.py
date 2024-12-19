from src.summarize.eda_tools import (
    get_all_csv,
    plot_sentiment_and_close,
)

df = get_all_csv(
    "/home/nicholas/gitrepos/ticker_sentiment/data/crypto/daily_discussions/all.csv"
)
ticker = "btc"
plot_sentiment_and_close(df, ticker)
