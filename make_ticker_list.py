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


# Function to extract valid tickers
def extract_valid_tickers_(sentence, tickers):
    potential_tickers = re.findall(r'\b[A-Z]{2,5}\b', sentence)
    [ticker for ticker in potential_tickers if ticker in tickers]


def get_words(sentence):
    cleaned_sentence = re.sub(r'[^\w\s]', '', sentence)
    words = cleaned_sentence.split()
    return words


def extract_valid_tickers(sentence, symbol_to_name_map, name_to_symbol_map):
    x = []
    for word in get_words(sentence):
        word = word.lower()
        if word in symbol_to_name_map:
            x += symbol_to_name_map[word]
        elif word in name_to_symbol_map:
            x += name_to_symbol_map[word]
    return x


# Example sentence
sentence = "Investing in BTC, DOGE, and some unknown currency like ABCD."

stn, nts = get_ticker_and_name_map()

result = extract_valid_tickers(sentence, stn, nts)

print(result)

stn["btc"]
