"""
MIT License

Copyright (c) 2023 Ulster University (https://www.ulster.ac.uk).
Project: Harmony (https://harmonydata.ac.uk)
Maintainer: Thomas Wood (https://fastdatascience.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import re
import numpy as np

from collections import Counter
from typing import List
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from harmony.schemas.responses.text import HarmonyCluster
import pathlib
from langdetect import detect, DetectorFactory
import os
DetectorFactory.seed = 0


folder_containing_this_file = pathlib.Path(__file__).parent.resolve()

stopwords_folder = f"{folder_containing_this_file}/../stopwords/"

stopwords_files = os.listdir(stopwords_folder)

lang_to_stopwords = {}
for stopwords_file in stopwords_files:
    with open(stopwords_folder + stopwords_file, "r", encoding="utf-8") as f:
        lang_to_stopwords[stopwords_file] = set(f.read().splitlines())

def generate_cluster_topics(
        clusters: List[HarmonyCluster],
        top_k_topics: int = 5,
    ) -> List[List[str]]:
    """
    Generate representative keywords/topics for clusters.

    Parameters
    ----------
    cluster_items : List[Question]
        The list of questions in the cluster.

    top_k_topics: int
        The number of topics to assign to each cluster.

    Returns
    -------
    List[List[str]]
        A list of the top k keywords representing each cluster.
    """
    # tokenise and count tokens
    re_tokenise = re.compile(r'(?i)([a-z][a-z]+)')
    token_counter = Counter()
    for cluster in clusters:
        tokens_in_cluster = set()
        for item in cluster.items:
            tokens = re_tokenise.findall(item.question_text.lower())
            for token in tokens:
                tokens_in_cluster.add(token)

        for token in tokens_in_cluster:
            token_counter[token] += 1

    # find inverse document frequencies (idf) of tokens
    num_clusters = len(clusters)
    idf = dict()
    for word, count in token_counter.items():
        idf[word] = np.log(num_clusters/count)

    # fit a multinomial naive bayes classifier
    vectoriser = CountVectorizer(lowercase=True, token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z]+\b')
    transformer = TfidfTransformer()
    nb = MultinomialNB()
    model = make_pipeline(vectoriser, transformer, nb)

    X = []
    y = []
    for cluster_id, cluster in enumerate(clusters):
        for item in cluster.items:
            X.append(item.question_text)
            y.append(cluster_id)

    model.fit(X, y)

    # detect langauge of the questions
    languages = set()
    for cluster in clusters:
        for item in cluster.items:
            try:
                lang = detect(item.question_text)
                languages.add(lang)
            except:
                pass

    # add the stopwords for each language
    stops = set()
    for language in languages:
        if language in lang_to_stopwords:
            stops = stops.union(lang_to_stopwords[language])

    # get class predictions
    vectoriser = model.named_steps['countvectorizer']
    transformer = model.named_steps['tfidftransformer']
    nb = model.named_steps['multinomialnb']

    fake_document = " ".join(vectoriser.vocabulary_)
    vectorised_document = vectoriser.transform([fake_document])
    transformed_document = transformer.transform(vectorised_document)

    probas = np.zeros((transformed_document.shape[1]))

    vocab_idx_to_string_lookup = [""] * transformed_document.shape[1]
    for w, i in vectoriser.vocabulary_.items():
        vocab_idx_to_string_lookup[i] = w

    transformed_documents = np.zeros((transformed_document.shape[1], transformed_document.shape[1]))
    for i in range(transformed_document.shape[1]):
        transformed_documents[i, i] = transformed_document[0, i]

    probas_for_vocab_and_class = nb.predict_log_proba(transformed_documents)

    # return the top k topics for each cluster
    topics = []
    for prediction_idx, label in enumerate(model.classes_):
        probas_this_class = probas_for_vocab_and_class[:, prediction_idx]

        top_vocab_idxes_this_class = np.argsort(-probas_this_class)

        questions_joined = ""
        for q in clusters[prediction_idx].items:
            questions_joined += q.question_text.lower() + " "

        top_topics = []
        for ctr, j in enumerate(top_vocab_idxes_this_class[:top_k_topics]):
            word = vocab_idx_to_string_lookup[j]
            if word not in stops and word in questions_joined:
                top_topics.append(word)
        topics.append(top_topics)

    return topics
