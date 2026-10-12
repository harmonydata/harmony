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

import os
import pathlib
from collections import Counter
from typing import List, Callable, Optional

import numpy as np
from numpy import dot, matmul, ndarray, matrix
from numpy.linalg import norm

from harmony.matching.deterministic_clustering import find_clusters_deterministic
from harmony.matching.affinity_propagation_clustering import cluster_questions_affinity_propagation
from harmony.matching.hdbscan_clustering import cluster_questions_hdbscan_from_embeddings
from harmony.matching.instrument_to_instrument_similarity import get_instrument_similarity
from harmony.matching.negator import negate
from harmony.schemas.requests.text import (
    Instrument,
    Question,
)
from harmony.schemas.responses.text import MatchResult
from harmony.schemas.text_vector import TextVector

from harmony.matching.kmeans_clustering import cluster_questions_kmeans_from_embeddings

from harmony.schemas.enums.clustering_algorithms import ClusteringAlgorithm
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0


# This has been tested on 16 GB RAM production server, 1000 seems a safe number (TW, 15 Dec 2024)
def get_batch_size(default=1000):
    try:
        batch_size = int(os.getenv("BATCH_SIZE", default))
        return max(batch_size, 0)
    except (ValueError, TypeError):
        return default

def is_empty_or_null_text(text: Optional[str]) -> bool:
    if text is None:
        return True
    if isinstance(text, str) and text.strip() == "":
        return True
    return False

def process_items_in_batches(items, llm_function):
    batch_size = get_batch_size()

    if batch_size == 0:
        return llm_function(items)

    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

    results = []
    for batch in batches:
        batch_results = llm_function(batch)
        results.extend(batch_results)
    return results


def cosine_similarity(vec1: ndarray, vec2: ndarray) -> ndarray:
    dp = dot(vec1, vec2.T)
    m1 = matrix(norm(vec1, axis=1))
    m2 = matrix(norm(vec2.T, axis=0))

    return np.asarray(dp / matmul(m1.T, m2))


def add_text_to_vec(text, texts_cached_vectors, text_vectors, is_negated_, is_query_) -> list[TextVector]:
    if text not in texts_cached_vectors:
        text_vectors.append(
            TextVector(
                text=text, vector=[], is_negated=is_negated_, is_query=is_query_
            )
        )
    else:
        vector = texts_cached_vectors[text]
        text_vectors.append(
            TextVector(
                text=text,
                vector=vector,
                is_negated=is_negated_,
                is_query=is_query_,
            )
        )
    return text_vectors


def get_question_languages(instruments: List[Instrument]) -> dict:
    """
    Map each question text to the language of the instrument it came from, so that negation uses the right rules.
    """
    question_languages = {}
    for instrument in instruments:
        language = getattr(instrument.language, "value", instrument.language) or "en"
        for question in instrument.questions:
            question_languages[question.question_text] = language
    return question_languages


def process_questions(questions: list, texts_cached_vectors: dict, is_negate: bool,
                      question_languages: Optional[dict] = None) -> list[TextVector]:
    if question_languages is None:
        question_languages = {}
    text_vectors: List[TextVector] = []
    for question_text in questions:
        # Skip None or whitespace-only texts
        if question_text is None or str(question_text).strip() == "":
            text_vectors.append(
                TextVector(
                    text=question_text,
                    vector=None,
                    is_negated=False,
                    is_query=False,
                )
            )
            continue

        # Normal non-empty case
        text_vectors = add_text_to_vec(question_text, texts_cached_vectors, text_vectors, False, False)

        if is_negate:
            negated_text = negate(question_text, question_languages.get(question_text, "en"))
        else:
            negated_text = question_text
        text_vectors = add_text_to_vec(negated_text, texts_cached_vectors, text_vectors, True, False)

    return text_vectors

def vectorise_texts(text_vectors, vectorisation_function):
    for index, text_dict in enumerate(text_vectors):
        if not text_dict.vector:
            text_vectors[index].vector = vectorisation_function([text_dict.text]).tolist()[0]
    return text_vectors


def vectors_pos_neg(text_vectors):
    vectors_pos = np.array(
        [
            x.vector
            for x in text_vectors
            if (x.is_negated is False and x.is_query is False)
        ]
    )

    # Create numpy array of negated texts vectors
    vectors_neg = np.array(
        [
            x.vector
            for x in text_vectors
            if (x.is_negated is True and x.is_query is False)
        ]
    )
    return vectors_pos, vectors_neg


def create_full_text_vectors(
        all_questions: List[str],
        query: Optional[str],
        vectorisation_function: Callable,
        texts_cached_vectors: dict[str, list[float]],
        is_negate: bool,
        question_languages: Optional[dict] = None
) -> tuple[List[TextVector], dict]:
    """
    Create full text vectors.
    """

    # Create a list of text vectors
    text_vectors = process_questions(all_questions, texts_cached_vectors, is_negate=is_negate,
                                     question_languages=question_languages)

    # Add query
    if query:
        text_vectors = add_text_to_vec(query, texts_cached_vectors, text_vectors, False, True)

    # Texts with no cached vector
    texts_not_cached = [x.text for x in text_vectors if not x.vector]

    # Get vectors for all texts not cached
    new_vectors_list: List = process_items_in_batches(texts_not_cached, vectorisation_function)

    # Create a dictionary with new vectors
    new_vectors_dict = {}
    for vector, text in zip(new_vectors_list, texts_not_cached):
        new_vectors_dict[text] = vector

    # Add new vectors to all_texts
    for index, text_dict in enumerate(text_vectors):
        if not text_dict.vector:
            new_vector: ndarray = new_vectors_list.pop(0)
            text_vectors[index].vector = new_vector.tolist()

    return text_vectors, new_vectors_dict





#
def match_instruments_with_function(
        instruments: List[Instrument],
        query: str,
        vectorisation_function: Callable,
        topics: List = [],
        mhc_questions: List = [],
        mhc_all_metadatas: List = [],
        mhc_embeddings: np.ndarray = np.zeros((0, 0)),
        texts_cached_vectors: dict[str, List[float]] = {},
        is_negate: bool = True,
        clustering_algorithm: ClusteringAlgorithm = ClusteringAlgorithm.affinity_propagation,
        num_clusters_for_kmeans: int = None,
        mhc_min_similarity: float = 0.0
) -> MatchResult:

    all_questions: List[Question] = []
    for instrument in instruments:
        all_questions.extend(instrument.questions)

    for question in all_questions:
        if question.question_text is None or question.question_text == "":
            raise ValueError("Invalid argument: you cannot send an empty question to Harmony. Please remove all null and empty questions.")
            
    text_vectors, new_vectors_dict = create_full_text_vectors(
        all_questions=[q.question_text for q in all_questions],
        query=query,
        vectorisation_function=vectorisation_function,
        texts_cached_vectors=texts_cached_vectors,
        is_negate=is_negate,
        question_languages=get_question_languages(instruments)
    )

    # get vectors for all original texts and vectors for negated texts
    vectors_pos, vectors_neg = vectors_pos_neg(text_vectors)

    # --- ✅ Query similarity (only if query is non-empty and vectors exist) ---
    if vectors_pos.size > 0 and query and query.strip():
        try:
            vector_query = np.array(
                [[x.vector for x in text_vectors if x.is_query][0]]
            )
            query_similarity = cosine_similarity(vectors_pos, vector_query)[:, 0]
        except Exception:
            query_similarity = np.array([])
    else:
        query_similarity = np.array([])

    # --- ✅ Pairwise similarity with polarity (only if valid vectors exist) ---
    if vectors_pos.size > 0:
        try:
            pairwise_similarity = cosine_similarity(vectors_pos, vectors_pos)

            # negated similarities
            pairwise_similarity_neg1 = cosine_similarity(vectors_neg, vectors_pos)
            pairwise_similarity_neg2 = cosine_similarity(vectors_pos, vectors_neg)
            pairwise_similarity_neg_mean = np.mean(
                [pairwise_similarity_neg1, pairwise_similarity_neg2], axis=0
            )

            # polarity calculation
            similarity_difference = pairwise_similarity - pairwise_similarity_neg_mean
            similarity_polarity = np.sign(similarity_difference)

            # treat very small diffs as 0 → force polarity to +1
            similarity_polarity[np.abs(similarity_difference) < 1e-3] = 1

            similarity_max = np.max(
                [pairwise_similarity, pairwise_similarity_neg_mean], axis=0
            )
            similarity_with_polarity = similarity_max * similarity_polarity
        except Exception:
            similarity_with_polarity = np.array([])
    else:
        similarity_with_polarity = np.array([])

    # --- ✅ Work out similarity with MHC ---
    if vectors_pos.size > 0 and len(mhc_embeddings) > 0:
        similarities_mhc = cosine_similarity(vectors_pos, mhc_embeddings)
        ctrs = {}

        # Build mask of valid MHC questions (non-empty text)
        valid_mhc_mask = np.array([
            bool(mhc_questions[i].question_text and len(mhc_questions[i].question_text.strip()) >= 3)
            for i in range(len(mhc_questions))
        ])

        for idx in range(len(all_questions)):
            # Get similarities for this question, masking out invalid MHC items
            masked_similarities = np.where(valid_mhc_mask, similarities_mhc[idx], -np.inf)
            mhc_item_idx = int(np.argmax(masked_similarities))
            strength_of_match = similarities_mhc[idx, mhc_item_idx]

            # Skip if no valid MHC items or similarity is below threshold
            if masked_similarities[mhc_item_idx] == -np.inf:
                continue
            if strength_of_match < mhc_min_similarity:
                continue

            question_text = mhc_questions[mhc_item_idx].question_text
            if all_questions[idx].instrument_id not in ctrs:
                ctrs[all_questions[idx].instrument_id] = Counter()
            for topic in mhc_all_metadatas[mhc_item_idx]["topics"]:
                ctrs[all_questions[idx].instrument_id][topic] += 1
            all_questions[idx].nearest_match_from_mhc_auto = mhc_questions[mhc_item_idx].model_dump()
            all_questions[idx].topics_strengths = {topic: float(strength_of_match)}

        instrument_to_category = {}
        for instrument_id, counts in ctrs.items():
            instrument_to_category[instrument_id] = []
            max_count = max(counts.values())
            for topic, topic_count in counts.items():
                if topic_count > max_count / 2:
                    instrument_to_category[instrument_id].append(topic)

        for question in all_questions:
            question.topics_auto = instrument_to_category.get(question.instrument_id, [])
    else:
        for question in all_questions:
            question.topics_auto = []

    # --- ✅ Instrument-to-instrument similarities ---
    instrument_to_instrument_similarities = get_instrument_similarity(instruments, similarity_with_polarity)

    # --- ✅ Clustering ---
    if similarity_with_polarity.size > 0:
        if clustering_algorithm == ClusteringAlgorithm.affinity_propagation:
            clusters = cluster_questions_affinity_propagation(all_questions, similarity_with_polarity)
        elif clustering_algorithm == ClusteringAlgorithm.deterministic:
            clusters = find_clusters_deterministic(all_questions, similarity_with_polarity)
        elif clustering_algorithm == ClusteringAlgorithm.kmeans:
            if num_clusters_for_kmeans is None:
                num_clusters_for_kmeans = int(np.floor(np.sqrt(len(all_questions))))
            clusters = cluster_questions_kmeans_from_embeddings(all_questions, vectors_pos, num_clusters_for_kmeans)
        elif clustering_algorithm == ClusteringAlgorithm.hdbscan:
            clusters = cluster_questions_hdbscan_from_embeddings(all_questions, vectors_pos)
        else:
            raise Exception("Invalid clustering algorithm")
    else:
        clusters = []  # fallback if no vectors

    # --- ✅ Response options similarity ---
    options = ["; ".join(q.options) for q in all_questions if q.options]
    if options:
        options_vectors = vectorisation_function(options)
        response_options_similarity = cosine_similarity(options_vectors, options_vectors).clip(0, 1)
    else:
        response_options_similarity = np.array([])

    # --- ✅ Topic tagging (only if topics and valid questions exist) ---
    if topics and all_questions:
        assigned_topics = {idx: [] for idx in range(len(all_questions))}
        question_topic_similarity_threshold = 0.7

        folder_containing_this_file = pathlib.Path(__file__).parent.resolve()
        stopwords_folder = f"{folder_containing_this_file}/../stopwords/"
        lang_to_stopwords = {}

        if os.path.exists(stopwords_folder):
            for stopwords_file in os.listdir(stopwords_folder):
                with open(os.path.join(stopwords_folder, stopwords_file), "r", encoding="utf-8") as f:
                    lang_to_stopwords[stopwords_file] = set(f.read().splitlines())

        for idx, question in enumerate(all_questions):
            if not question.question_text or not question.question_text.strip():
                continue

            words = question.question_text.split()
            try:
                lang = detect(question.question_text)
            except Exception:
                lang = None

            stopwords = lang_to_stopwords.get(lang, [])
            words = [word for word in words if word not in stopwords]

            if words:
                question_vector = vectorisation_function(words)
                topics_vectors = vectorisation_function(topics)
                sim = cosine_similarity(question_vector, topics_vectors).clip(0, 1)

                for j in range(sim.shape[1]):
                    if np.any(sim[:, j] >= question_topic_similarity_threshold):
                        assigned_topics[idx].append(topics[j])

        for idx, q_topics in assigned_topics.items():
            all_questions[idx].topics = q_topics

    return MatchResult(
        questions=all_questions,
        similarity_with_polarity=similarity_with_polarity,
        response_options_similarity=response_options_similarity,
        query_similarity=query_similarity,
        new_vectors_dict=new_vectors_dict,
        instrument_to_instrument_similarities=instrument_to_instrument_similarities,
        clusters=clusters
    )
