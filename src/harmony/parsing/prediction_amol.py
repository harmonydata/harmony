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

import os
import pandas as pd
import sys
import re
import json

import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
# from tensorflow.keras.models import load_model
from sklearn.base import BaseEstimator, TransformerMixin
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
from torch import nn, optim
from sklearn.preprocessing import FunctionTransformer
import torch
from transformers import BertTokenizerFast
from transformers import AutoModelForTokenClassification
from transformers import pipeline
# Default local path for harmony models
local_path = os.getenv("HARMONY_MODELS_PATH", os.path.expanduser("~") + "/harmony")

####Loading models
ner_model_path = os.path.join(local_path, "ner_model")
tokenizer_path = os.path.join(local_path, "tokenizer")
print(ner_model_path)
model_fine_tuned = AutoModelForTokenClassification.from_pretrained(ner_model_path)
bert_tokenizer = BertTokenizerFast.from_pretrained(tokenizer_path)
nlp = pipeline("ner", model=model_fine_tuned, tokenizer=bert_tokenizer)

tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
class LSTMClassifier(nn.Module):
    def __init__(self, hidden_dim, output_dim):
        super(LSTMClassifier, self).__init__()
        self.encoder = AutoModel.from_pretrained('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        for param in self.encoder.parameters():
            param.requires_grad = False
        self.lstm = nn.LSTM(self.encoder.config.hidden_size, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, output_dim)

    def forward(self, input_ids, attention_mask=None):
        with torch.no_grad():
            embedded = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        _, (hidden, _) = self.lstm(embedded)
        output = self.fc(torch.cat((hidden[-2,:,:], hidden[-1,:,:]), dim = 1))
        return output
    
sentence_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')  
def create_embeddings(X):
    return np.array(sentence_model.encode(X, show_progress_bar=True))

with open(os.path.join(local_path, "json_xgb.pkl"), 'rb') as file:
            json_model = pickle.load(file)

with open(os.path.join(local_path, "stack_model_with_undersampling.pkl"), 'rb') as file:
                text_model = pickle.load(file)

model  = LSTMClassifier(128, 1)
model.load_state_dict(torch.load(os.path.join(local_path, "model.pth"), map_location=torch.device('cpu')))
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device) 

#####Loading models completed

def bert_prediction(questions):

    all_questions = []
    for question in questions:
        ner_results = nlp(question)
        # Initialize variables to store the current question and all questions
        current_question = []


        # Iterate through each entity in the NER results
        for entity in ner_results:
            word = entity['word']
            entity_type = entity['entity']

            # Handle token continuation marked by '##'
            if word.startswith('##'):
                word = word[2:]  # Remove '##'
                if current_question:
                    current_question[-1] += word  # Append directly to the last word
                continue

            # Handle new question starting
            if entity_type == 'B-QUESTION':
                # If there's an ongoing question, store it first
                if current_question:
                    all_questions.append("".join(current_question).strip())
                    current_question = []
                # Add the new word to start a fresh question
                current_question.append(word)
            elif entity_type == 'I-QUESTION':
                # Correct spacing issues for punctuation
                if word in {',', '.', ';', ':'}:
                    if current_question and not current_question[-1].endswith(' '):
                        current_question[-1] += word  # Append punctuation directly to the last word
                else:
                    # Ensure proper spacing for words
                    if current_question and not current_question[-1].endswith(' '):
                        word = ' ' + word
                    current_question.append(word)

        # Append the last question if not empty
        if current_question:
            all_questions.append("".join(current_question).strip())
    return all_questions

def predict_new_text(model, text, tokenizer, device):
    # Tokenize the input text and convert to a tensor
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)

    # Get model predictions
    with torch.no_grad():
        outputs = model(input_ids, attention_mask)

    # Apply sigmoid function to get the probability
    probabilities = torch.sigmoid(outputs).squeeze()

    # Convert to numpy and return
    return probabilities.cpu().numpy()

def txt_to_df(lines):
    # Remove newline characters from each line
    cleaned_lines = [line.strip() for line in lines]

    df = pd.DataFrame(cleaned_lines, columns=['Text'])

    # print(f"Converted text to dataframe")
    return df
def combine_text_rows(df):
    combined_text = []
    current_text = ''
    df["Text"] = df["Text"].fillna('')
    for _, row in df.iterrows():
        if row['Text'] != '':
            current_text += str(row['Text']) + ' '
            
        else:
            if current_text != '':
                combined_text.append(current_text.strip())
                current_text = ''
    
    # If there's remaining text after the loop ends
    if current_text != '':
        combined_text.append(current_text.strip())
    
    combined_df = pd.DataFrame({'Text': combined_text})
    return combined_df
def preprocess_json(json_data):
    data = json_data

    # Prepare data for DataFrame
    df_data = []

    # Iterate over each table in the JSON file
    for table_number, table_info in enumerate(data, start=1):
        table_data = table_info['tables']

        # Iterate over each cell in the table
        for row in table_data:
            for cell in row:
                df_data.append({
                    'Cell Data': cell,
                    'Table Number': table_number
                })

    # Create DataFrame
    df = pd.DataFrame(df_data)
    return df

def predict_json(text_list):
    # Generate embeddings for the input text
    embeddings = create_embeddings(text_list)
    # Use the trained classifier to predict
    predictions = json_model.predict(embeddings)
    return predictions

def predict_text(text_list):
    # Generate embeddings for the input text
    embeddings = create_embeddings(text_list)
    # Use the trained classifier to predict
    predictions = text_model.predict(embeddings)
    return predictions

def find_questions(text, json_data, lstm=False):
    final_questions = []
    if len(json_data) > 0 and len(json_data) > 0:
        #try:
            
        json_df = preprocess_json(json_data)
        # Load the model from the pickle file
        print(json_df)
        if not json_df.empty:
            y_pred_json = predict_json(json_df['Cell Data'].tolist())
            y_pred_series = pd.Series(y_pred_json)
            questions = json_df[y_pred_series == 1]
            questions['Cell Data'] = questions['Cell Data'].str.strip()

            final_questions = questions['Cell Data'].tolist()
            # print(final_questions)
    
    df = txt_to_df(text)
    df = combine_text_rows(df)
    #regex to find questions
    # pattern = r'(^.*(?:who|what|when|where|why|how|\?)$)|(^\d+\.\sI.*\.$)'
    # df['Text'] = df['Text'].str.strip()
    # mask_df = df['Text'].str.contains(pattern, regex=True)
    # valid_questions = df[mask_df]
    # final_questions.extend(valid_questions['Text'].tolist())
    # df = df[~mask_df]
    if not df.empty:
        if lstm:
             # Ensure model is on the correct device
            texts = df['Text'].tolist()
            threshold = 0.4
            temp_questions = []
            for text in texts:
                probabilities = predict_new_text(model, text, tokenizer, device)
                predicted_class = int(probabilities > threshold)
                if predicted_class == 1:
                    temp_questions.append(text)
            final_questions.extend(temp_questions)
            # print(final_questions)
        else:
            y_pred_text = predict_text(df['Text'].tolist())
            df["y_pred_series"] = list(y_pred_text)
            questions = df[df.y_pred_series == 1]
            final_questions.extend(questions['Text'].tolist())
    # except:
    #     print("Error in text")
    # print("final question before bert=====>", final_questions)
    # print("length of first element", len(final_questions[0]))
    final_questions = bert_prediction(final_questions)
    return list(set(final_questions))


def extract_questions(pdf_plain_text: str, tables_as_dict: list) -> list:
    '''
    Placeholder function for extracting questionnaire items from a PDF
    '''
    predictions = []
    pdf_plain_text = pdf_plain_text.splitlines()
    predictions = find_questions(pdf_plain_text, tables_as_dict, lstm=True)
    print("predictions===>",predictions)
    
    return predictions
    # return "\n".join(["\t" + re.sub(r'\s+', ' ', p) + "\t" for p in predictions])
