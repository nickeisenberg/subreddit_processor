from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

tokenizer = AutoTokenizer.from_pretrained("Jean-Baptiste/roberta-ticker")
model = AutoModelForTokenClassification.from_pretrained("Jean-Baptiste/roberta-ticker")

nlp = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")

nlp("goog is going to the moon")
  
nlp("I am going to eat a cake tomorrow")
