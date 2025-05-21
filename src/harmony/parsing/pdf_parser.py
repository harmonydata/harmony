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

import torch
from harmony.parsing.util.tika_wrapper import parse_pdf_to_list
from harmony.schemas.requests.text import RawFile, Instrument
from tqdm import tqdm
from transformers import AutoModelForTokenClassification, AutoTokenizer

import harmony

# Disable tokenizer parallelism
# os.environ["TOKENIZERS_PARALLELISM"] = "false"

print("Starting to load pretrained model... harmonydata/debertaV2_pdfparser")
model = AutoModelForTokenClassification.from_pretrained("harmonydata/debertaV2_pdfparser")

print("Starting to load pretrained tokeniser... harmonydata/debertaV2_pdfparser")
tokenizer = AutoTokenizer.from_pretrained("harmonydata/debertaV2_pdfparser")
print("Loaded pretrained model and tokeniser.")


def predict(text):
    inputs = tokenizer(
        text,
        return_offsets_mapping=True,
        return_overflowing_tokens=True,
        truncation=True,
        padding="max_length",
        max_length=512,
        stride=128,
        add_special_tokens=True,
        return_tensors="pt",
    ).to(model.device)

    n = len(inputs["input_ids"])  # type: ignore

    all_questions = []
    all_answers = []

    done = set()

    tokens_found = []

    with torch.inference_mode():
        for i in range(n):
            predictions = torch.argmax(
                model(
                    input_ids=inputs["input_ids"][i: i + 1],  # type: ignore
                    attention_mask=inputs["attention_mask"][i: i + 1],  # type: ignore
                ).logits,
                dim=2,
            )

            for t, (start, end) in zip(
                    predictions[0], inputs["offset_mapping"][i]  # type: ignore
            ):
                if (start, end) in done or (start == 0 and end == 0):
                    continue

                done.add((start, end))

                predicted_token_class = model.config.id2label[t.item()]

                tokens_found.append((int(start), int(end), predicted_token_class))

    grouped_spans = {"answer": [], "question": []}

    prev_cls = None
    span = []
    for start_char, end_char, cls in tokens_found:
        if cls != prev_cls and len(span) > 0:
            if prev_cls == "answer" or prev_cls == "question":
                grouped_spans[prev_cls].append(span)
            span = []
        span.append(start_char)
        span.append(end_char)
        prev_cls = cls

    # Add final token and class to respective key in dictionary
    if len(span) > 0 and (prev_cls == "answer" or prev_cls == "question"):
        grouped_spans[prev_cls].append(span)

    all_texts = {"question": [], "answer": []}
    for item_type in ["question", "answer"]:
        for span in grouped_spans[item_type]:
            first_char = min(span)
            last_char = max(span)
            token_text = text[first_char:last_char]
            all_texts[item_type].append((first_char, last_char, token_text))

    return all_texts["question"], all_texts["answer"]


def clean_question_text(question_text):
    question_text = re.sub(r'\s+', ' ', question_text)
    question_text = question_text.strip()
    return question_text


def convert_pdf_to_instruments(file: RawFile) -> Instrument:
    # file is an object containing these properties:
    # content: str - The raw file contents so if it's a PDF this is a byte sequence in base 64 encoding
    # text_content: str - this is empty but we will use Tika to populate this in this method
    # tables: list - this is a list of all the tables in the document. The front end has populated this field.

    if not file.text_content:
        pages = parse_pdf_to_list(file.content)  # call Tika to convert the PDF to plain text
        file.text_content = "\n".join(pages)
    else:
        pages = [file.text_content]
        pages = [file.text_content]

    # Run prediction script to return questions and answers from file text content

    question_texts_entire_document = []
    answer_texts_entire_document = []

    chunks_of_text = []
    batch_size = 10
    for batch_start in range(0, len(pages), batch_size):
        batch_end = batch_start + batch_size
        if batch_end > len(pages):
            batch_end = len(pages)
        batch_of_pages = pages[batch_start:batch_end]
        chunks_of_text.append("\n".join(batch_of_pages))

    for page in tqdm(chunks_of_text):
        all_questions, all_answers = predict(page)

        question_texts = [q[2] for q in all_questions]
        answer_texts = [None] * len(question_texts)
        for idx in range(len(answer_texts)):
            answer_texts[idx] = []

        for answer_start_char_idx, answer_end_char_idx, answer_text in all_answers:
            question_idx = 0
            for question_idx, (question_start_char_idx, question_end_char_idx, _) in enumerate(all_questions):
                if question_start_char_idx < answer_start_char_idx:
                    break

            for answer_text_individual_line in answer_text.split("\n"):
                # Split response options on line breaks
                answer_text_individual_line = answer_text_individual_line.strip()
                if len(answer_text_individual_line) > 0 and len(answer_texts[question_idx]) < 10:
                    answer_texts[question_idx].append(answer_text_individual_line)

        for answer_idx, this_block_of_answers in enumerate(answer_texts):
            if len(this_block_of_answers) == 0 and answer_idx > 0 and len(answer_texts[answer_idx - 1]) > 0:
                this_block_of_answers.extend(answer_texts[answer_idx - 1])

        question_texts_entire_document.extend(question_texts)
        answer_texts_entire_document.extend(answer_texts)

    question_texts_entire_document = [clean_question_text(q) for q in question_texts_entire_document]

    instrument = harmony.create_instrument_from_list(question_texts_entire_document, answer_texts_entire_document,
                                                     instrument_name=file.file_name,
                                                     file_name=file.file_name)
    return [instrument]
