from src.summarize.eda_tools import (
    get_all_csv, 
    plot_sentiment_and_close,
)

df = get_all_csv()
ticker = "ada"
plot_sentiment_and_close(df, ticker)
