from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)

from transformers import pipeline


def get_fin_bert():
    model_name = "ProsusAI/finbert"
    return pipeline(
        task="sentiment-analysis", 
        model=AutoModelForSequenceClassification.from_pretrained(model_name), 
        tokenizer=AutoTokenizer.from_pretrained(model_name)
    )


model = get_fin_bert()
x = "BTC is a shit coin"
result = model(x)
print(result)
