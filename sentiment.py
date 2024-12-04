from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    pipeline
)

from transformers import pipeline


# Load FinBERT model
model_name = "ProsusAI/finbert"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Set up pipeline
sentiment_pipeline = pipeline(
    task="sentiment-analysis", model=model, tokenizer=tokenizer
)

# Analyze WSB comment
x = "BTC is a shit coin"
result = sentiment_pipeline(x)
print(result)
