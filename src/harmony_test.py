import harmony
import numpy as np
#harmony.download_models()
from harmony import match_instruments
#from harmony.schemes.requests.text import Instrument
#from harmony import match_instruments
#
def main():
    questions = ["how old are your dogs", "which year were you born","I like your hair","what is your email address"]
    vectorisation_function = harmony.matching.default_matcher.convert_texts_to_vector
    text_vectors = harmony.matching.matcher.process_questions(questions)
#    text_vectors = harmony.matching.matcher.vectorise_texts(text_vectors,vectorisation_function)
#    harmony.matching.matcher.texts_similarity_matrix_benchmark(text_vectors)
#



#main()






