import operator

import numpy as np

from harmony.schemas.responses.text import InstrumentToInstrumentSimilarity


def get_precision_recall_f1(item_to_item_similarity_matrix: np.ndarray) -> tuple:
    abs_similarities_between_instruments = np.abs(item_to_item_similarity_matrix)

    coord_to_sim = {}
    for y in range(abs_similarities_between_instruments.shape[0]):
        for x in range(abs_similarities_between_instruments.shape[1]):
            coord_to_sim[(y, x)] = abs_similarities_between_instruments[y, x]

    best_matches = set()
    is_used_x = set()
    is_used_y = set()
    for (y, x), sim in sorted(coord_to_sim.items(), key=operator.itemgetter(1), reverse=True):
        if x not in is_used_x and y not in is_used_y and abs_similarities_between_instruments[(y, x)] >= 0:
            best_matches.add((x, y))

            is_used_x.add(x)
            is_used_y.add(y)

    precision = len(is_used_x) / abs_similarities_between_instruments.shape[1]
    recall = len(is_used_y) / abs_similarities_between_instruments.shape[0]

    f1 = np.mean((precision, recall))

    return precision, recall, f1


def get_instrument_similarity(instruments, similarity_with_polarity):
    instrument_start_pos = []
    instrument_end_pos = []
    cur_start = 0
    for instr_idx in range(len(instruments)):
        instrument_start_pos.append(cur_start)
        instrument_end_pos.append(cur_start + len(instruments[instr_idx].questions))
        cur_start += len(instruments[instr_idx].questions)

    instrument_to_instrument_similarities = []

    for i in range(len(instruments)):
        instrument_1 = instruments[i]
        for j in range(i + 1, len(instruments)):
            instrument_2 = instruments[j]
            item_to_item_similarity_matrix = similarity_with_polarity[instrument_start_pos[i]:instrument_end_pos[i],
                                             instrument_start_pos[j]:instrument_end_pos[j]]

            precision, recall, f1 = get_precision_recall_f1(item_to_item_similarity_matrix)

            instrument_to_instrument_similarities.append(
                InstrumentToInstrumentSimilarity(instrument_1_idx=i, instrument_2_idx=j,
                                                 instrument_1_name=instrument_1.instrument_name,
                                                 instrument_2_name=instrument_2.instrument_name, precision=precision,
                                                 recall=recall, f1=f1)
            )

    return instrument_to_instrument_similarities
