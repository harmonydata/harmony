import spacy
import joblib
import spacy
nlp = spacy.blank("en")

crf = joblib.load(f'/media/thomas/642d0db5-2c98-4156-b591-1a3572c5868c/projects_client/wellcome/pdf_extraction_experiments/05_ner/05_crf_model')

import numpy as np


import nltk
import sklearn
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn_crfsuite as crfsuite
from sklearn_crfsuite import metrics
import pandas as pd

def word2features(sent, i):
    word = sent[i][0]
    postag = sent[i][1]
    features = [
        'bias',
        'word.text=' + word.text,
        'word.lower=' + word.norm_,
        'word[-3:]=' + word.text[-3:],
        'word[-2:]=' + word.text[-2:],
        'word.isupper=%s' % word.is_upper,
        'word.istitle=%s' % word.is_title,
        'word.isdigit=%s' % word.is_digit,
        'word.isnewline=%s' % word.is_space,
        'word.length=%s' % len(word.text),
        'postag=' + postag
    ]
    if i > 0:
        word1 = sent[i - 1][0]
        postag1 = sent[i - 1][1]
        features.extend([
            '-1:word.isnewline=%s' % word1.is_space,
        ])
    else:
        features.append('BOS')

    num_previous_words_found = 1
    for j in range(i - 1, 1, -1):
        if num_previous_words_found > 3:
            break
        word1 = sent[j][0]
        postag1 = sent[j][1]
        if not word1.is_space:
            features.extend([
                f'-{num_previous_words_found}:word.text=' + word1.text,
                f'-{num_previous_words_found}:word.lower=' + word1.norm_,
                f'-{num_previous_words_found}:word.istitle=%s' % word1.is_title,
                f'-{num_previous_words_found}:word.isupper=%s' % word1.is_upper,
                f'-{num_previous_words_found}:word.isdigit=%s' % word1.is_digit,
                f'-{num_previous_words_found}:word.length=%s' % len(word1.text),
                f'-{num_previous_words_found}:postag=' + postag1
            ])
            num_previous_words_found += 1

    num_following_words_found = 1
    for j in range(i + 1, len(sent)):
        if num_following_words_found > 3:
            break
        word1 = sent[j][0]
        postag1 = sent[j][1]
        if not word1.is_space:
            features.extend([
                f'+{num_following_words_found}:word.text=' + word1.text,
                f'+{num_following_words_found}:word.lower=' + word1.norm_,
                f'+{num_following_words_found}:word.istitle=%s' % word1.is_title,
                f'+{num_following_words_found}:word.isupper=%s' % word1.is_upper,
                f'+{num_following_words_found}:word.isdigit=%s' % word1.is_digit,
                f'+{num_following_words_found}:word.length=%s' % len(word1.text),
                f'+{num_following_words_found}:postag=' + postag1
            ])
            num_following_words_found += 1

    if i < len(sent) - 1:
        word1 = sent[i + 1][0]
        postag1 = sent[i + 1][1]
        features.extend([
            '+1:word.isnewline=%s' % word1.is_space,
        ])
    else:
        features.append('EOS')

    if i < len(sent) - 2:
        word2 = sent[i + 2][0]
        postag2 = sent[i + 2][1]
        features.extend([
            '+2:word.isnewline=%s' % word2.is_space,
        ])

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]


def sent2labels(sent):
    return [label for token, postag, label in sent]


def sent2tokens(sent):
    return [token for token, postag, label in sent]

def convert_to_tuples(df_train_or_test):
    l = []
    lookup = {0:"O", 1:"B", 2:"I"}
    for i in range(len(df_train_or_test)):
        l.append((df_train_or_test.text.iloc[i], "N", lookup[df_train_or_test.y.iloc[i]]))
    return l

def annotate_document(page_text):
    doc = nlp(page_text)

    candidates = list(doc)

    df = pd.DataFrame({"text": candidates, "y": 0, "file": ""})

    test_sents = [convert_to_tuples(df)]

    X_test = [sent2features(s) for s in test_sents]

    y_pred = crf.predict(X_test)

    token_classes = np.zeros((len(doc, )))

    for i in range(len(doc)):
        if y_pred[0][i] == "B":
            token_classes[i] = 1
        elif y_pred[0][i] == "I":
            token_classes[i] = 2

    return token_classes