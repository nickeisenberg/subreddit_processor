import re
import string
from praw.reddit import Comment


def remove_all_non_asci(text: str):
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    text = re.sub("\n", " ", text)
    text = re.sub(r"[^\x00-\x7F]", "", text)
    text = re.sub(r"\w*emote\w*", "", text)
    text = re.sub(r"\b\w{31,}\b", "", text).strip()
    return text


def lower_text_and_remove_all_non_asci(text):
    return remove_all_non_asci(text.lower().strip())


def get_default_comment_processer(max_len: int = 512):
    def _(comment: str | Comment):
        comment_txt = comment.body if isinstance(comment, Comment) else comment
        processed_text = lower_text_and_remove_all_non_asci(comment_txt)
        return processed_text if len(processed_text) <= max_len else ""

    return _


if __name__ == "__main__":
    pass
