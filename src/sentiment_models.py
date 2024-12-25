from typing import Callable
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
from transformers import pipeline


def get_finbert(device="cpu") -> Callable[[str], tuple[str, float]]:
    model_name = "ProsusAI/finbert"
    finbert_pipeline = pipeline(
        task="sentiment-analysis", 
        model=AutoModelForSequenceClassification.from_pretrained(model_name).to(device),
        tokenizer=AutoTokenizer.from_pretrained(model_name),
        device=device
    )
    def finbert_(sentence: str):
        sent: dict = finbert_pipeline(sentence)[0]
        finbert_pipeline.call_count = 0
        return sent["label"], sent["score"]
    return finbert_


def get_vader(neg_cutoff: float = -.1, 
              pos_cutoff: float = .1) -> Callable[[str], tuple[str, float]]:
    sid_obj = SentimentIntensityAnalyzer()
    def vader_(sentence: str):
        sentiment_dict = sid_obj.polarity_scores(sentence)
        compound = sentiment_dict['compound']
        if compound >= pos_cutoff :
            return "positive", compound
        elif compound <= neg_cutoff :
            return "negative", -1 * compound
        else:
            if compound > 0:
                return "neutral", compound
            else:
                return "neutral", -1 * compound
    return vader_


if __name__ == "__main__":
    finbert = get_finbert()
    vader = get_vader()
    sentence = "btc is saving me"
    vader(sentence)
    finbert(sentence)
    sentence = "btc is shit"
    vader(sentence)
    finbert(sentence)

