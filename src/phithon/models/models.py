from abc import ABC, abstractmethod
from typing import Callable, Literal

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .utils import huggingface_sentiment_analysis_pipeline


class SentimentModel(ABC):
    @abstractmethod
    def __call__(
        self, *args, **kwargs
    ) -> tuple[Literal["positive", "neutral", "negative"], float]:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class TwitterRobertaBase(SentimentModel):
    def __init__(self, device):
        self.device = device
        self.model = huggingface_sentiment_analysis_pipeline(
            "cardiffnlp/twitter-roberta-base-sentiment-latest", device
        )

    def __call__(self, sentence: str):
        return self.model(sentence)

    @property
    def name(self):
        return "twitter_roberta_base"


class FinBERT(SentimentModel):
    def __init__(self, device):
        self.device = device
        self.model = huggingface_sentiment_analysis_pipeline("ProsusAI/finbert", device)

    def __call__(self, sentence: str):
        return self.model(sentence)

    @property
    def name(self):
        return "finbert"


class DistilRoberta(SentimentModel):
    def __init__(self, device):
        self.device = device
        self.model = huggingface_sentiment_analysis_pipeline(
            "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis",
            device=device,
        )

    def __call__(self, sentence: str):
        return self.model(sentence)

    @property
    def name(self):
        return "distil_roberta"


class Vader(SentimentModel):
    def __init__(self, negative_cutoff: float = -0.1, positive_cutoff: float = 0.1):
        self.negative_cutoff = negative_cutoff
        self.positive_cutoff = positive_cutoff
        self.model = self.get_vader(negative_cutoff, positive_cutoff)

    def __call__(self, sentence: str):
        return self.model(sentence)

    @property
    def name(self):
        return "vader"

    @staticmethod
    def get_vader(
        neg_cutoff: float = -0.1, pos_cutoff: float = 0.1
    ) -> Callable[[str], tuple[Literal["positive", "neutral", "negative"], float]]:
        sid_obj = SentimentIntensityAnalyzer()

        def vader_(sentence: str):
            sentiment_dict = sid_obj.polarity_scores(sentence)
            compound = sentiment_dict["compound"]
            if compound >= pos_cutoff:
                return "positive", compound
            elif compound <= neg_cutoff:
                return "negative", -1 * compound
            else:
                if compound > 0:
                    return "neutral", compound
                else:
                    return "neutral", -1 * compound

        return vader_
