import spacy

nlp = spacy.load("en_core_web_sm")

text = input("Enter text: ")

doc = nlp(text)

for ent in doc.ents:
    print(ent.text, "->", ent.label_) 
