'''
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

'''

import re

re_starts_number = re.compile(r'^\d')
re_starts_lc = re.compile(r'^[a-z]')
re_starts_uc = re.compile(r'^[A-Z]')


def get_seq_type(bullet_text):
    if re_starts_number.match(bullet_text):
        seq_type = "number"
        value = int(re.sub(r'\D.*', '', bullet_text))
    elif re_starts_lc.match(bullet_text):
        seq_type = "lowercase"
        value = ord(bullet_text[0:1]) - 96
    elif re_starts_uc.match(bullet_text):
        seq_type = "uppercase"
        value = ord(bullet_text[0:1]) - 65
    else:
        seq_type = bullet_text[0:1]
        value = int(re.sub(r'\D', '', bullet_text))
    if len(seq_type) > 1 and bullet_text[-1:] in (")", "."):
        seq_type = seq_type + bullet_text[-1:]
    return seq_type, value


def find_longest_uninterrupted_sequence(bullet_texts: list) -> list:
    running_sequences = []
    for idx in range(len(bullet_texts)):
        bullet_text = bullet_texts[idx]
        if bullet_text is not None:
            seq_type, value = get_seq_type(bullet_text)
            candidate_sequences = []
            for test_sequence in reversed(running_sequences):
                previous_idx, previous_seq_type, previous_value = test_sequence[-1]
                # and value in (previous_value, previous_value + 1) \
                if previous_seq_type == seq_type \
                        and bullet_texts[idx] != bullet_texts[previous_idx]:
                    candidate_sequences.append(test_sequence)

            if len(candidate_sequences) > 0:
                sequence_to_append_to = sorted(candidate_sequences, key=lambda s: len(s) + s[-1][0] / 1000, reverse=True)[0]
            else:
                sequence_to_append_to = []
                running_sequences.append(sequence_to_append_to)
            sequence_to_append_to.append((idx, seq_type, value))

    if len(running_sequences) > 0:
        sequences_long_to_short = sorted(running_sequences, key=lambda s: len(s), reverse=True)
        longest_sequence = sequences_long_to_short[0]
        longest_sequence_length = len(longest_sequence)
        if len(sequences_long_to_short) > 1:
            for seq in sequences_long_to_short[1:]:
                if len(seq) * 2 > longest_sequence_length:
                    longest_sequence.extend(seq)
    else:
        longest_sequence = None
    return longest_sequence
