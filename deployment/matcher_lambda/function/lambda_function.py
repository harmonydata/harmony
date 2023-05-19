import json
import os
import pickle as pkl
from collections import Counter

import numpy as np
import requests

from harmony.matching.matcher import match_instruments_with_function
from harmony.schemas.requests.text import MatchBody, Question
from harmony.schemas.responses.text import MatchResponse
from pydantic import parse_obj_as

headers = {
    'Content-Type': 'application/json'
}

mhc_questions = []
mhc_all_metadatas = []
mhc_embeddings = np.zeros((0, 0))

DATA_PATH = "/mnt/efs"

try:
    with open(DATA_PATH + "/mhc_questions.json",
              "r", encoding="utf-8") as f:
        for l in f:
            mhc_question = Question.parse_raw(l)
            mhc_questions.append(mhc_question)
    with open(
            DATA_PATH + "/mhc_all_metadatas.json",
            "r", encoding="utf-8") as f:
        for l in f:
            mhc_meta = json.loads(l)
            mhc_all_metadatas.append(mhc_meta)
    with open(DATA_PATH + "/mhc_embeddings.npy",
              "rb") as f:
        mhc_embeddings = np.load(f)
except:
    print("Could not load MHC embeddings ", str(os.getcwd()))

print("Loaded embeddings", len(mhc_embeddings))

CACHE_FILE = DATA_PATH + "/harmony_vectors_cache.pkl"

item_to_vectors_cache = {}
invocation_counter = Counter()

if os.path.isfile(CACHE_FILE):
    try:
        with open(CACHE_FILE, "rb") as f:
            item_to_vectors_cache = pkl.load(f)
    except:
        print("Could not load cache")


def vectorisation_function(all_texts: np.ndarray) -> np.ndarray:
    # Work out which texts aren't in the cache.
    indices_to_calculate = []
    calculation_lookup = {}
    for idx, text in enumerate(all_texts):
        if text not in item_to_vectors_cache:
            calculation_lookup[idx] = len(indices_to_calculate)
            indices_to_calculate.append(idx)

    # If there are any non-cached items, we call the neural network.
    if len(indices_to_calculate) > 0:
        if len(indices_to_calculate) == len(all_texts):
            texts_to_send_to_neural_network = all_texts
        else:
            texts_to_send_to_neural_network = all_texts[indices_to_calculate, :]

        API_URL = os.environ.get("VECTOR_API_URL", "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        headers = {"Authorization": "Bearer " + os.environ.get("VECTOR_API_KEY", "")}

        response = requests.post(API_URL, headers=headers, json={"inputs": texts_to_send_to_neural_network, "options": {"wait_for_model": True}})

        print ("RESPONSE IS ", response, response.text)

        response_vectors = np.asarray(response.json())

        for idx, text in enumerate(texts_to_send_to_neural_network):
            item_to_vectors_cache[text] = response_vectors[idx, :]

        invocation_counter[0] += 1
        if invocation_counter[0] % 5 == 0:
            try:
                with open(CACHE_FILE, "wb") as f:
                    pkl.dump(item_to_vectors_cache, f)
            except:
                print("Could not save cache")

        # all items came from API
        if len(indices_to_calculate) == len(all_texts):
            return response_vectors

        items = []
        for idx, text in enumerate(all_texts):
            if idx in calculation_lookup:
                items.append(response_vectors[calculation_lookup, :])
            else:
                items.append(item_to_vectors_cache[text])

        return np.asarray(items, dtype=np.float32)

    else:
        # all items came from cache
        items = []
        for text in all_texts:
            items.append(item_to_vectors_cache[text])

        return np.asarray(items, dtype=np.float32)


def lambda_handler(event, context):
    print(json.dumps(event))

    match_body = parse_obj_as(MatchBody, json.loads(event))

    instruments = match_body.instruments
    query = match_body.query

    all_questions, similarity_with_polarity, query_similarity = match_instruments_with_function(instruments, query,
                                                                                                vectorisation_function,
                                                                                                mhc_questions,
                                                                                                mhc_all_metadatas,
                                                                                                mhc_embeddings)

    matches_jsonifiable = similarity_with_polarity.tolist()

    if query_similarity is not None:
        query_similarity = query_similarity.tolist()

    response = MatchResponse(questions=all_questions, matches=matches_jsonifiable, query_similarity=query_similarity)

    return response.json()
