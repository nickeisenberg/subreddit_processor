from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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


# Function to print sentiments of the sentence.
def sentiment_scores(sentence):

    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()

    # polarity_scores method of SentimentIntensityAnalyzer object gives a sentiment dictionary.
    # which contains pos, neg, neu, and compound scores.
    sentiment_dict = sid_obj.polarity_scores(sentence)
    
    print("Overall sentiment dictionary is : ", sentiment_dict)

    # print("Sentence was rated as ", sentiment_dict['neg']*100, "% Negative")
    # print("Sentence was rated as ", sentiment_dict['neu']*100, "% Neutral")
    # print("Sentence was rated as ", sentiment_dict['pos']*100, "% Positive")

    print("Sentence Overall Rated As", end=" ")

    # Decide sentiment as positive, negative, or neutral
    if sentiment_dict['compound'] >= 0.05 :
        print("Positive")
    elif sentiment_dict['compound'] <= -0.05 :
        print("Negative")
    else :
        print("Neutral")

finbert = get_fin_bert()

sentence = "btc sucks dick"
sentiment_scores(sentence)
finbert(sentence)
