import pandas as pd
import numpy as np
import re
import html
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
from functools import lru_cache
import spacy
from spacy.cli import download as spacy_download


@lru_cache(maxsize=1)
def get_nlp():
    try:
        return spacy.load("en_core_web_sm", disable=["parser", "ner"])
    except OSError:
        # se non c'è, scaricalo e ricarica
        spacy_download("en_core_web_sm")
        return spacy.load("en_core_web_sm", disable=["parser", "ner"])

def clean_html_and_normalize(text: str) -> str:
    """Rimuove HTML, decode entità, normalizza spazi e minuscole."""
    if pd.isna(text) or not isinstance(text, str):
        return ""
    text = re.sub(r'(<br\s*/?>)+', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize_and_lemmatize(text: str, min_len=2, remove_stop=True) -> list[str]:
    """Tokenizza, rimuove stopword/punteggiatura, fa lemmatizzazione."""
    nlp = get_nlp()
    doc = nlp(text)
    tokens = []
    for tok in doc:
        if remove_stop and tok.is_stop:
            continue
        if tok.is_punct or tok.is_space:
            continue
        lemma = tok.lemma_.lower()
        if len(lemma) < min_len:
            continue
        if lemma.isnumeric():
            continue
        tokens.append(lemma)
    return tokens

def join_tokens(tokens: list[str]) -> str:
    return " ".join(tokens)

def top_n_terms_corpus(corpus: list[str], n=20):
    counter = Counter()
    for doc in corpus:
        counter.update(doc.split())
    return counter.most_common(n)

def compute_tfidf_features(texts: list[str], max_features=2000):
    """Restituisce matrice TF-IDF e il vettorizzatore (con tokenizer custom)."""
    vectorizer = TfidfVectorizer(
        tokenizer=lambda t: tokenize_and_lemmatize(t),
        preprocessor=clean_html_and_normalize,
        max_features=max_features
    )
    tfidf_matrix = vectorizer.fit_transform(texts)
    return tfidf_matrix, vectorizer

def top_tfidf_terms_for_doc(row_idx, matrix, vectorizer, top_k=10):
    feature_array = np.array(vectorizer.get_feature_names_out())
    row = matrix[row_idx].toarray().flatten()
    top_indices = row.argsort()[::-1][:top_k]
    return list(zip(feature_array[top_indices], row[top_indices]))


def to_float(x):
    try:
        return float(x)
    except:
        return np.nan
    
