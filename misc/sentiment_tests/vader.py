from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_vader():
    sid_obj = SentimentIntensityAnalyzer()
    def vader_(sentence):
        sentiment_dict = sid_obj.polarity_scores(sentence)
        compound = sentiment_dict['compound']
        if compound >= 0.05 :
            return "positive"
        elif compound <= -0.05 :
            return "negative", -1 * compound
        else:
            if compound > 0:
                return "neutral", compound
            else:
                return "neutral", -1 * compound
    return vader_


vader = get_vader()
sentence = "btc sucks dick"

vader(sentence)
