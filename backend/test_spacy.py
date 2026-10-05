import spacy

nlp = spacy.load("en_core_web_sm")

text = input("Enter text: ")

doc = nlp(text)

print("\nDetected Entities:")

if doc.ents:
    for ent in doc.ents:
        print(f"{ent.text} --> {ent.label_}")
else:
    print("No entities detected.")