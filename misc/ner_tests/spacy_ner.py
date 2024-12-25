import spacy

# Load a pre-trained spaCy NER model
nlp = spacy.load('en_core_web_sm')

# Example sentence
sentence = "Tesla is building a Gigafactory in Texas."

# Process the sentence through the NER model
doc = nlp(sentence)

# Extract and display named entities
for ent in doc.ents:
    print(f"Entity: {ent.text}, Label: {ent.label_}")

