from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)
from transformers import pipeline


def get_fin_bert(device="cpu"):
    model_name = "ProsusAI/finbert"
    return pipeline(
        task="sentiment-analysis", 
        model=AutoModelForSequenceClassification.from_pretrained(model_name).to(device),
        tokenizer=AutoTokenizer.from_pretrained(model_name),
        device=device
    )
