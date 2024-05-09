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

# Load the pretrained Sentence Transformer model
model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
sentence_model = SentenceTransformer(model_name)


class SentenceTransformerEmbedder(BaseEstimator, TransformerMixin):
    def __init__(self, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        self.model = SentenceTransformer(model_name)
        
    def fit(self, X, y=None):
        return self  # nothing to fit
    
    def transform(self, X):
        # Convert texts to embeddings
        embeddings = self.model.encode(X, show_progress_bar=True)
        return np.array(embeddings)
    
# Function to preprocess text data using Sentence Transformer
def get_embeddings(sentences):
    return sentence_model.encode(sentences, batch_size=64, show_progress_bar=True)

def txt_to_df(lines):
    # Remove newline characters from each line
    cleaned_lines = [line.strip() for line in lines]

    df = pd.DataFrame(cleaned_lines, columns=['Text'])

    print(f"Converted text to dataframe")
    return df
def combine_text_rows(df):
    combined_text = []
    combined_other = []
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

def find_questions(text, json_data, lstm=False):
    final_questions = []
    if len(json_data) > 0 and len(json_data) > 0:
        #try:
            
        json_df = preprocess_json(json_data)
        # Load the model from the pickle file
        with open(r'C:\Users\tates\Classwork\open-source\pdf-questionnaire-extraction-main (1)\pdf-questionnaire-extraction-main\data\models/json_xgb.pkl', 'rb') as file:
            json_model = pickle.load(file)
        y_pred_json = json_model.predict(json_df['Cell Data'].tolist())
        y_pred_series = pd.Series(y_pred_json)
        questions = json_df[y_pred_series == 1]
        questions['Cell Data'] = questions['Cell Data'].str.strip()

        final_questions = questions['Cell Data'].tolist()
            # print(final_questions)
        #except:
        #    print("Error in json")
    ################text##########################
    #try:
    
    if True:
        df = txt_to_df(text)
        df = combine_text_rows(df)
        #regex to find questions
        pattern = r'(^.*(?:who|what|when|where|why|how|\?)$)|(^\d+\.\sI.*\.$)'
        df['Text'] = df['Text'].str.strip()
        mask_df = df['Text'].str.contains(pattern, regex=True)
        valid_questions = df[mask_df]
        final_questions.extend(valid_questions['Text'].tolist())
        df = df[~mask_df]
        if not df.empty:
            if lstm:
                model_file_path = r'models/lstm_with_undersampling.keras'
                model = load_model(model_file_path)

                predict_embeddings = get_embeddings(df['Text'].tolist())
                predict_embeddings = np.expand_dims(predict_embeddings, axis=1)
                y_pred = model.predict(predict_embeddings)

                mask = (y_pred > 0.75).astype(int)
                mask = mask.flatten()

                # Create a boolean Series with the same index as df
                y_pred_series = pd.Series(mask, index=df.index)

                # Filter the DataFrame using boolean indexing
                questions = df[y_pred_series == 1]
                
                final_questions.extend(questions['Text'].tolist())
                # print(final_questions)
            else:
                with open(r'C:\Users\tates\Classwork\open-source\pdf-questionnaire-extraction-main (1)\pdf-questionnaire-extraction-main\data\models/stack_model_with_undersampling.pkl', 'rb') as file:
                    text_model = pickle.load(file)
                y_pred_text = text_model.predict(df['Text'].tolist())
                df["y_pred_series"] = list(y_pred_text)
                questions = df[df.y_pred_series == 1]
                final_questions.extend(questions['Text'].tolist())
    # except:
    #     print("Error in text")
    return list(set(final_questions))


def extract_questions(pdf_plain_text: str, tables_as_dict: list) -> str:
    '''
    Placeholder function for extracting questionnaire items from a PDF
    '''
    predictions = []
    predictions = find_questions(pdf_plain_text, tables_as_dict, lstm=False)
    # if len(tables_as_dict) > 0:
    #     if len(tables_as_dict['pageTables']) == 1:
    #         for table in tables_as_dict['pageTables'][0]:
    #             for row in table:
    #                 col = row[0].strip()
    #                 if re.findall("[a-z]", col):
    #                     predictions.append("\t" + col)
    # if len(predictions) > 0:
    #     return "\n".join(predictions)
    # else:
    #     for line in pdf_plain_text.split("\n"):
    #         line = re.sub(r'\s+', ' ', line).strip()
    #         line = re.sub(r'\n+', '', line)
    #         line = re.sub(r'^\d+\.?', '', line).strip()
    #         predictions.append("\t" + line)
    return "\n".join(["\t" + re.sub(r'\s+', ' ', p) + "\t" for p in predictions])


# test_files = ["000_mfqchildselfreportshort.txt",
# "001_patienthealthquestionnaire.txt",
# "004_newyorklongitudinalstudybythom.txt",
# "005_beckdepressioninventorybdi.txt",
# "006_apadsm5severitymeasurefordepre.txt",
# "007_bhrcsselfreportedscared.txt",
# "008_gad7anxietyupdated0.txt",
# "009_validationoftheportugueseversi.txt",
# "011_bhrcsparentreportsocialaptitud.txt",
# "012_hrcw2protocolopsicoconfmenor18.txt",
# "013_hrcw2protocolopsicoadultos.txt",
# "014_testedeansiedadegad7dranadimme.txt",
# "015_hrcw1dom.txt",
# "016_hrcw2protocolodomiciliarmenor1.txt",
# "019_bhrcsparentreportsocialcohesio.txt",
# "021_sdqenglishukpt417single.txt",
# "023_hrcw1psico.txt",
# "024_bhrcsselfreportedmfq.txt",
# "026_sf36.txt",
# "030_bhrcsselfreportedwarwickedinbr.txt",
# "031_ghq12.txt",
# "032_bhrcsparentreportsdqchild.txt",
# "034_bhrcsparentreportsocialcohesio.txt",
# "037_hrcw0dom.txt",
# "039_selfmeasuresforlonelinessandin.txt",
# "045_mr0510201tb.txt",
# "046_borderlinepersonalityscreener.txt",
# "047_bhrcsparentreportsdqadult.txt",
# "055_beta_retirement.txt",
# "062_eoin_no_numbers.txt",
# "064_hrcw1psicoconf.txt"]

# COMMAND_LINE_PARAM = f"Usage: python create_sample_submission.py train|test"

# if len(sys.argv) < 2:
#     DATASET = "train"
# else:
#     DATASET = sys.argv[1]

# if DATASET != "train" and DATASET != "test":
#     print(COMMAND_LINE_PARAM)
#     exit()

# if DATASET == "test":
#     txt_files_to_process = test_files
#     output_file = "submission_amol.csv"
# else:
#     txt_files_to_process = os.listdir("preprocessed_text")
#     output_file = "train_predictions_amol.csv"
# all_json_files = set(os.listdir("preprocessed_tables"))

# ids = []
# predictions = []
# for txt_file in txt_files_to_process:
#     print(txt_file)
#     # if "eoin" not in txt_file:
#     #     continue
#     json_file = re.sub(r'txt$', 'json', txt_file)
#     with open("preprocessed_text/" + txt_file, "r", encoding="utf-8") as f:
#         file_in_plain_text = f.readlines()
#     if json_file in all_json_files:
#         with open("preprocessed_tables/" + json_file, "r", encoding='utf-8') as f:
#             file_in_json = f.read()
#         tables_as_dict = json.loads(file_in_json)
#     else:
#         tables_as_dict = {}
#     predictions.append(extract_questions(file_in_plain_text, tables_as_dict))
#     ids.append(txt_file)
# df = pd.DataFrame()
# df["ID"] = ids
# df["predict"] = predictions

# print ("Writing predictions to", output_file)
# df.to_csv(output_file, index=False)