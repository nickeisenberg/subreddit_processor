from src.summarize.eda_tools import (
    get_all_csv,
    plot_sentiment_and_close,
)

from src.summarize.crypto import get_crypto_ticker_finder 

from src.sentiment_models import get_fin_bert

df = get_all_csv(
    "/home/nicholas/gitrepos/ticker_sentiment/data/crypto/daily_discussions/all.csv"
)
ticker = "ada"
plot_sentiment_and_close(df, ticker)

finbert = get_fin_bert()

finbert("Bitcoin is fucking up my whole portfolio")

finbert("BTC is going to make a strong rally in quarter 3")

finder = get_crypto_ticker_finder(100)

finbert("bitcoin, cardano and eth are the best coins. I love them")

finder("bitcoin, cardano and eth are the best coins. I love them")
