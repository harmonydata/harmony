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

import json
import re

re_word = re.compile(r'(?i)(\S+)')

re_initial_num = re.compile(r'(^\d+)')
re_contains_num = re.compile(r'\d')
re_initial_num_dot = re.compile(r'(^\d+\.)')
re_alpha = re.compile(r'(^[a-zA-Z]+)')
re_bracket = re.compile(r'(?:\(|\))')


def convert_text_to_features(text):
    token_texts = []
    token_start_char_indices = []
    token_end_char_indices = []
    token_properties = []

    char_indices_of_newlines = set()
    for idx, c in enumerate(text):
        if c == "\n":
            char_indices_of_newlines.add(idx)

    char_indices_of_question_marks = set()
    for idx, c in enumerate(text):
        if c == "?":
            char_indices_of_question_marks.add(idx)

    tokens = list(re_word.finditer(text))

    this_token_properties = {}

    for token in tokens:
        is_number = len(re_initial_num.findall(token.group()))
        is_number_dot = len(re_initial_num_dot.findall(token.group()))
        num_nums = len(re_contains_num.findall(token.group()))
        is_alpha = len(re_alpha.findall(token.group()))
        is_bracket = len(re_bracket.findall(token.group()))

        dist_to_prev_newline = token.start()
        for c in range(token.start(), 1, -1):
            if c in char_indices_of_newlines:
                dist_to_prev_newline = token.start() - c
                break

        dist_to_next_question_mark = len(text) - token.start()
        for c in range(token.start(), len(text)):
            if c in char_indices_of_question_marks:
                dist_to_next_question_mark = c - token.start()
                break

        is_capital = int(token.group()[0] != token.group()[0].lower())

        is_letters_and_numbers = int(is_alpha and num_nums > 0)

        this_token_properties = {"length": len(token.group()), "is_number": is_number,
                                 "is_alpha": is_alpha,
                                 "is_capital": is_capital,
                                 "is_letters_and_numbers": is_letters_and_numbers,
                                 "is_bracket": is_bracket,
                                 "is_number_dot": is_number_dot,
                                 "num_nums": num_nums,
                                 "dist_to_prev_newline": dist_to_prev_newline,
                                 "dist_to_next_question_mark": dist_to_next_question_mark,
                                 "char_index": token.start()}

        token_texts.append(token.group())
        token_start_char_indices.append(token.start())
        token_end_char_indices.append(token.end())
        token_properties.append(this_token_properties)

    all_property_names = list(sorted(this_token_properties))

    for idx in range(len(token_properties)):
        focus_dict = token_properties[idx]
        # Generate features including prev and next token.
        # There was no increase in performance associated with increasing this window. (TW 19/07/2024)
        for offset in range(-1, 2):
            if offset == 0:
                continue
            j = idx + offset
            if j >= 0 and j < len(token_properties):
                offset_dict = token_properties[j]
            else:
                offset_dict = {}

            for property_name in all_property_names:
                focus_dict[f"{property_name}_{offset}"] = offset_dict.get(property_name, 0)

    return token_texts, token_start_char_indices, token_end_char_indices, token_properties


if __name__ == "__main__":
    test_text = "this is a test123 a)"
    token_texts, token_start_char_indices, token_end_char_indices, token_properties = convert_text_to_features(
        test_text)
    print(token_texts)
    print(token_start_char_indices)
    print(token_end_char_indices)
    print(json.dumps(token_properties, indent=4))
