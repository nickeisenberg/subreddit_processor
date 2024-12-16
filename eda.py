import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Fetch historical data for BTC-USD
btc_data = yf.download(
    'BTC-USD', start='2020-01-01', end='2024-12-31', interval='1d'
)

if btc_data is not None:
    print(btc_data.head())

btc_data.columns.get_level_values(0)

plt.plot(btc_data["Close"].values)
plt.show()
