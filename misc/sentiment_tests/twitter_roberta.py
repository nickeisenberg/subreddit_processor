from transformers import pipeline
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig


MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
device = "cpu"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL).to(device)

sentiment_task = pipeline(
    "sentiment-analysis", model=model, tokenizer=tokenizer, device=device
)

text = "BTC is killing it right now"
sentiment_task(text)

