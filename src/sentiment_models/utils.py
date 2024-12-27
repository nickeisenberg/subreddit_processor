from typing import Any, Callable, cast
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
from transformers import pipeline


def huggingface_sentiment_analysis_pipeline(
        model_name, device="cpu") -> Callable[[str], tuple[str, float]]:
    sent_pipeline = cast(Any, pipeline(
        task="sentiment-analysis", 
        model=AutoModelForSequenceClassification.from_pretrained(model_name).to(device),
        tokenizer=AutoTokenizer.from_pretrained(model_name),
        device=device
    ))
    def _(sentence: str) -> tuple[str, float]:
        sent: dict = sent_pipeline(sentence)[0]
        sent_pipeline.call_count = 0
        return sent["label"], sent["score"]
    return _
