from harmony.matching.matcher import match_instruments_with_catalogue_instruments
from harmony.schemas.requests.text import Instrument, Question
import numpy as np

def dummy_vectorisation(texts):
    vector_size = 12  
    
    # Predefined vectors for known texts
    random_vectors = {
        "What is your age?": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "How old are you?": [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "What is your name?": [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "What is your favorite color?": [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    
    # Assign a random vector for unknown texts
    random_unknown_vector = lambda: np.random.rand(vector_size).tolist()

    # Generate vectors
    vectors = [
        random_vectors.get(text, random_unknown_vector())  
        for text in texts
    ]
    return np.array(vectors)

# Sample instruments for testing
sample_instruments = [
    Instrument(
        instrument_id="1",
        questions=[Question(question_text="What is your age?", instrument_id="1")],
    ),
    Instrument(
        instrument_id="2",
        questions=[Question(question_text="How old are you?", instrument_id="2")],
    ),
    Instrument(
        instrument_id="3",
        questions=[Question(question_text="What is your name?", instrument_id="3")],
    ),
    Instrument(
        instrument_id="4",
        questions=[Question(question_text="What is your favorite color?", instrument_id="4")],
    ),
]

# Sample catalogue data
sample_catalogue_data = {
    "questions": [
        Question(question_text="What is your age?", instrument_id="catalogue_1"),
        Question(question_text="How old are you?", instrument_id="catalogue_2"),
        Question(question_text="What is your name?", instrument_id="catalogue_3"),
        Question(question_text="What color do you like?", instrument_id="catalogue_4"),
    ],
    "instrument_idx_to_question_idx": [[0], [1], [2], [3]],
    "all_embeddings_concatenated": np.array([
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Embedding for "What is your age?"
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Embedding for "How old are you?"
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Embedding for "What is your name?"
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # Embedding for "What color do you like?"
    ]),
    "all_instruments": [
        {"instrument_name": "Catalogue Instrument 1", "metadata": {"source": "CATALOGUE", "url": "", "sweep_id": ""}},
        {"instrument_name": "Catalogue Instrument 2", "metadata": {"source": "CATALOGUE", "url": "", "sweep_id": ""}},
        {"instrument_name": "Catalogue Instrument 3", "metadata": {"source": "CATALOGUE", "url": "", "sweep_id": ""}},
        {"instrument_name": "Catalogue Instrument 4", "metadata": {"source": "CATALOGUE", "url": "", "sweep_id": ""}},
    ],
    "all_questions": ["What is your age?", "How old are you?", "What is your name?", "What color do you like?"],
}


# Cached vectors for efficiency
cached_vectors = {}

# Test with within_instrument=True (Task 4 enabled)
print("=== Test with Within Instrument Matches Enabled ===")
match_instruments_with_catalogue_instruments(
    instruments=sample_instruments,
    catalogue_data=sample_catalogue_data,
    vectorisation_function=dummy_vectorisation,
    texts_cached_vectors=cached_vectors,
    within_instrument=True,
    save_crosswalk=True,
)

# Test with within_instrument=False (Task 4 disabled)
print("\n=== Test with Within Instrument Matches Disabled ===")
match_instruments_with_catalogue_instruments(
    instruments=sample_instruments,
    catalogue_data=sample_catalogue_data,
    vectorisation_function=dummy_vectorisation,
    texts_cached_vectors=cached_vectors,
    within_instrument=False,
    save_crosswalk=True,
)


