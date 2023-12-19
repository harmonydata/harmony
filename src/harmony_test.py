import harmony
import numpy as np
#harmony.download_models()
from harmony import match_instruments
#from harmony.schemes.requests.text import Instrument
#from harmony import match_instruments
#
import json

def import_():
    instruments = []
    with open("mhc_data/mhc_questions.json", "r", encoding="utf-8") as f:
        for l in f:
            instrument = json.loads(l)
            instruments.append(instrument)
    return instruments

def texts_similarity_matrix_benchmark(text_vectors):
        # Create numpy array of texts vectors
        # Get similarity with polarity
        vectors_pos,vectors_neg = harmony.matching.matcher.vectors_pos_neg(text_vectors)
        if vectors_pos.any():
            pos_pairwise_similarity = harmony.matching.matcher_utils.cosine_similarity(vectors_pos, vectors_pos)
        return pos_pairwise_similarity

def test_similarity():
    questions = ["I was bothered by things that usually don’t bother me.","I did not feel like eating; my appetite was poor.","I felt that I could not shake off the blues even with help from my family or friends.","I felt I was just as good as other people."]
    questions = ["lost my key", "found my car"]
    vectorisation_function = harmony.matching.default_matcher.convert_texts_to_vector
    text_vectors = harmony.matching.matcher.process_questions(questions)
    print(text_vectors)
    text_vectors = harmony.matching.matcher.vectorise_texts(text_vectors,vectorisation_function)
    print(texts_similarity_matrix_benchmark(text_vectors))
#   pip install harmonydata

def test_match_instruments_with_function():
    instruments = import_()
    print(instruments[0])
    query = "Lost much sleep over worry?"
    vectorisation_function = harmony.matching.default_matcher.convert_texts_to_vector
    all_questions, similarity_with_polarity, query_similarity, new_vectors_dict=harmony.matching.matcher.match_instruments_with_function(instruments[1:10],query,vectorisation_function,[],[],np.zeros((0, 0)),{})
    print(all_questions)
    print(similarity_with_polarity)
#    print(query_similarity)
#    print(new_vectors_dict)
    np.savetxt("sim_with_polarity.txt", similarity_with_polarity, fmt='%d', delimiter='\t')




test_match_instruments_with_function()





