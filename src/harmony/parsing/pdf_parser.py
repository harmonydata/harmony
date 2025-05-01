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

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

import harmony
from harmony.parsing.util.tika_wrapper import parse_pdf_to_plain_text
from harmony.schemas.requests.text import RawFile, Instrument


def group_token_spans_by_class(tokens, classes, tokenizer) -> dict:
    """
    Given a list of tokens, and a list of predicted classes
    for each token, create a dictionary to hold each
    span of tokens.
    Example:
        > group_token_spans_by_classes(['How', 'are', 'you', '?', 'Alright'],
                                        ['question', 'question', 'question', 'question', 'answer'],
                                        bert_tokenizer)
        > {"question":["How are you?"], "answer":["Alright"]}

    :param tokens: List of tokens
    :type tokens: List[str]
    :param classes: List of predicted classes
    :type classes: List[str]
    :param tokenizer: Tokenizer
    :return: Dictionary of each span relative to its class
    """
    grouped_spans = {"answer": [], "question": [], "other": []}
    span = []
    prev_cls = None

    for token, cls in zip(tokens, classes):
        if cls != prev_cls and span:
            grouped_spans[prev_cls].append(tokenizer.convert_tokens_to_string(span))
            span = []
        span.append(token)
        prev_cls = cls
    # Add final token and class to respective key in dictionary
    if span:
        grouped_spans[prev_cls].append(tokenizer.convert_tokens_to_string(span))

    return grouped_spans


def predict(test_text):
    # Load fine-tuned huggingface model and tokenizer
    model = AutoModelForTokenClassification.from_pretrained("harmonydata/debertaV2_pdfparser")
    tokenizer = AutoTokenizer.from_pretrained("harmonydata/debertaV2_pdfparser")

    # Tokenize input text
    tokenized_texts = tokenizer(test_text, return_tensors="pt")

    # Inference with tokenized input text
    with torch.no_grad():
        logits = model(**tokenized_texts).logits

    # Retrieve predicted class for each token
    predictions = torch.argmax(logits, dim=2)
    predicted_token_class = [model.config.id2label[t.item()] for t in predictions[0]]

    # Get input IDs (tensor) and convert to list
    input_ids = tokenized_texts["input_ids"][0].tolist()
    # Convert input IDs to tokens
    decoded_tokenized_texts = tokenizer.convert_ids_to_tokens(input_ids)

    # Remove leading [CLS] and trailing [SEP] tokens from decoded
    # tokens, and the list of predictions
    predicted_token_class = predicted_token_class[1:-1]
    decoded_tokenized_texts = decoded_tokenized_texts[1:-1]

    grouped_tokens = group_token_spans_by_class(decoded_tokenized_texts, predicted_token_class, tokenizer)

    return grouped_tokens


def convert_pdf_to_instruments(file: RawFile) -> Instrument:
    # file is an object containing these properties:
    # content: str - The raw file contents so if it's a PDF this is a byte sequence in base 64 encoding
    # text_content: str - this is empty but we will use Tika to populate this in this method
    # tables: list - this is a list of all the tables in the document. The front end has populated this field.

    if not file.text_content:
        file.text_content = parse_pdf_to_plain_text(file.content)  # call Tika to convert the PDF to plain text

    questions_from_text = predict(file.text_content)["question"]

    instrument = harmony.create_instrument_from_list(questions_from_text, instrument_name=file.file_name,
                                                     file_name=file.file_name)
    return [instrument]
