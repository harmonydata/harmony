import harmony
import numpy as np
#harmony.download_models()
from harmony import match_instruments
#from harmony.schemes.requests.text import Instrument
#from harmony import match_instruments
#
def main():
    questions = ["occupation", "job"]
    vectorisation_function = harmony.matching.default_matcher.convert_texts_to_vector
    text_vectors = harmony.matching.matcher.process_questions(questions)
    text_vectors = harmony.matching.matcher.vectorise_texts(text_vectors,vectorisation_function)
    harmony.matching.matcher.texts_similarity_matrix(text_vectors)




main()





#    instruments = harmony.example_instruments["CES_D English"], harmony.example_instruments["GAD-7 English"]
#    print(type(instruments[0].language))
#    questions, similarity, query_similarity, new_vectors_dict = harmony.match_instruments(instruments)
#    print(instruments[0])
#    a = harmony.matching.matcher.cosine_similarity(np.random.rand(2,2),np.random.rand(2,2))
 
