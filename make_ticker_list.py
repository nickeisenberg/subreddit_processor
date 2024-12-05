from collections import defaultdict
import re
from pycoingecko import CoinGeckoAPI

def get_ticker_and_name_map():
    sym_to_name = defaultdict(list)
    name_to_sym = defaultdict(list)
    cg = CoinGeckoAPI()
    cryptos = cg.get_coins_list()
    for crypto in cryptos:
        sym = crypto["symbol"].lower()
        name = crypto["name"].lower()
        sym_to_name[sym].append(name)
        name_to_sym[name].append(sym)
    return sym_to_name, name_to_sym


stn, nts = get_ticker_and_name_map()
stn["btc"]
nts["bitcoin"]

# Function to extract valid tickers
def extract_valid_tickers(sentence, tickers):
    # Regex to match words that resemble tickers
    potential_tickers = re.findall(r'\b[A-Z]{2,5}\b', sentence)
    # Validate against known tickers
    return [ticker for ticker in potential_tickers if ticker in tickers]

# Example sentence
sentence = "Investing in BTC, DOGE, and some unknown currency like ABCD."

# Extract valid tickers
result = extract_valid_tickers(sentence, crypto_tickers)
print(result)

