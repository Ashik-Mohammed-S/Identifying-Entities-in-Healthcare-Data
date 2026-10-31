"""Exercise the declared NLP stack without the original healthcare dataset."""
import pandas as pd
import spacy
import sklearn_crfsuite

frame = pd.DataFrame({"word": ["test", "other"], "label": ["A", "B"]})
assert frame.shape == (2, 2)
nlp = spacy.load("en_core_web_sm")
assert len(nlp("This is a test.")) > 0
crf = sklearn_crfsuite.CRF(max_iterations=5)
crf.fit([[{"word": "test"}], [{"word": "other"}]], [["A"], ["B"]])
assert len(crf.predict([[{"word": "test"}]])) == 1

print("NLP stack smoke checks passed.")
