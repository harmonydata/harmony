"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from sentence_transformers import SentenceTransformer
import numpy as np


model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def handler(event, context):
    body = json.loads(event["body"])
    print ("body is", body)
    texts = np.asarray(body["texts"])
    embeddings = model.encode(texts)
    embeddings_jsonifiable = embeddings.tolist()
    response = {
        "statusCode": 200,
        "body": embeddings_jsonifiable
    }
    return response
