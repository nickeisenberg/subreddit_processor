import re
import string


def remove_all_non_asci(text: str):
    text = re.sub(f"[{re.escape(string.punctuation)}]", '', text)
    text = re.sub("\n", " ", text)
    text = re.sub(r'[^\x00-\x7F]', '', text)
    text = re.sub(r"\w*emote\w*", "", text)
    text = re.sub(r'\b\w{31,}\b', "", text).strip()
    return text


def lower_text_and_remove_all_non_asci(text):
    return remove_all_non_asci(text.lower().strip())


def default_text_processor(max_len: int = 512):
    def _(text: str):
        processed_text = lower_text_and_remove_all_non_asci(text)
        return processed_text if len(processed_text) <= max_len else ""
    return _


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


if __name__ == "__main__":
    processor = default_text_processor(10)
    processor("here is a wall of text")
