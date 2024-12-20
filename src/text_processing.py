import re
import string
from pycoingecko import CoinGeckoAPI


def remove_all_non_asci(text: str):
    text = re.sub(f"[{re.escape(string.punctuation)}]", '', text)
    text = re.sub("\n", " ", text)
    text = re.sub(r'[^\x00-\x7F]', '', text)
    text = re.sub(r"\w*emote\w*", "", text)
    text = re.sub(r'\b\w{31,}\b', "", text).strip()
    return text


def lower_text_and_remove_all_non_asci(text: str):
    return remove_all_non_asci(text.lower().strip())


def get_ticker_and_name_map(top: int):
    sym_to_sym = {}
    name_to_sym = {}
    cg = CoinGeckoAPI()
    cryptos = cg.get_coins_markets(
        vs_currency='usd', order='market_cap_desc', per_page=top, page=1
    )
    for crypto in cryptos:
        sym = crypto["symbol"].lower()
        name = crypto["name"].lower()
        sym_to_sym[sym] = sym
        name_to_sym[name] = sym
    return sym_to_sym, name_to_sym


def get_tickers_from_string(sentence: str, symbol_to_name_map: dict, 
                            name_to_symbol_map: dict) -> list[str]:
    x = []
    for word in lower_text_and_remove_all_non_asci(sentence).split():
        word = word.lower()
        if word in symbol_to_name_map:
            x.append(symbol_to_name_map[word])
        elif word in name_to_symbol_map:
            x.append(name_to_symbol_map[word])
    return list(set(x))
