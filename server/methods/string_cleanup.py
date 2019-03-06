import re

def remove_articles(text):
  return re.sub(r'\s*(a|an|and|the)(\s+)', ' ', text)

def remove_punctuation(text):
	return re.sub(r'[.,\/#!$%\^&\*;:{}=\-_`~()]', ' ', text)
