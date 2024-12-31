from abc import ABC, abstractmethod
from typing import Callable, Literal
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from src.sentiment_models.utils import huggingface_sentiment_analysis_pipeline


def get_finbert(device="cpu"):
    """
    returns 'ProsusAI/finbert'
    """
    return huggingface_sentiment_analysis_pipeline("ProsusAI/finbert", device)


def get_twitter_roberta_base(device="cpu"):
    """
    returns 'cardiffnlp/twitter-roberta-base-sentiment-latest'
    """
    return huggingface_sentiment_analysis_pipeline(
        "cardiffnlp/twitter-roberta-base-sentiment-latest", device
    )


def get_fin_distilroberta_base(device="cpu"):
    """
    returns 'mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis'
    """
    return huggingface_sentiment_analysis_pipeline(
        "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
        device=device
    )


def get_vader(neg_cutoff: float = -.1, 
              pos_cutoff: float = .1) -> Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]]:
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
