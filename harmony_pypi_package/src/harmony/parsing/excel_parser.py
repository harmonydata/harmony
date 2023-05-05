import traceback
import uuid
from typing import List

import numpy as np
import pandas as pd
from langdetect import detect

from harmony.parsing.util.excel_to_pandas import parse_excel_to_pandas
from harmony.schemas.requests.text import Question
from harmony.schemas.requests.text import RawFile, Instrument


def clean_option_no(option_could_be_int):
    if option_could_be_int is None \
            or pd.isna(option_could_be_int) or pd.isnull(option_could_be_int):
        return ""
    if type(option_could_be_int) is str:
        return option_could_be_int
    if (type(option_could_be_int) is float or type(option_could_be_int) is np.float64 or type(
            option_could_be_int) is np.float32) \
            and option_could_be_int.is_integer():
        return str(int(option_could_be_int))
    return str(option_could_be_int)


def convert_excel_to_instruments(file: RawFile) -> List[Instrument]:
    sheet_name_to_dataframe = parse_excel_to_pandas(file.content)

    instruments = []
    for sheet_idx, (sheet_name, df_questions) in enumerate(sheet_name_to_dataframe.items()):

        # check we have 3 columns. If more or less, adjust it by deleting or inserting.
        if len(df_questions.columns) > 3:
            if str(df_questions[df_questions.columns[3]].iloc[0]).lower() == "filename":
                if len(df_questions.columns) > 4 and str(
                        df_questions[df_questions.columns[4]].iloc[0]).lower() == "language":
                    df_questions.drop(columns=df_questions.columns[5:], inplace=True)
                else:
                    df_questions.drop(columns=df_questions.columns[4:], inplace=True)
            else:
                df_questions.drop(columns=df_questions.columns[3:], inplace=True)
        elif len(df_questions.columns) < 3:
            col_avg_lengths = [0] * len(df_questions.columns)
            for col_idx, col_name in enumerate(df_questions.columns):
                col_avg_lengths[col_idx] = df_questions[col_name].apply(lambda s: len(str(s))).mean()
            biggest_col = int(np.argmax(col_avg_lengths))
            if biggest_col == 0:
                df_questions.insert(0, "question_no", [str(n) for n in range(len(df_questions))])
            if len(df_questions.columns) < 3:
                df_questions.insert(2, "options", [""] * len(df_questions))

        # standardise the column names
        if len(df_questions.columns) == 3:
            df_questions.columns = ["question_no", "question", "options"]
        elif len(df_questions.columns) == 4:
            df_questions.columns = ["question_no", "question", "options", "filename"]
        else:
            df_questions.columns = ["question_no", "question", "options", "filename", "language"]

        # Check if header row present, in which case remove it
        rows_to_delete = []
        for i in range(len(df_questions)):
            if df_questions.question.iloc[i] is None or type(df_questions.question.iloc[i]) is not str or \
                    df_questions.question.iloc[i].lower() in ["question", "text",
                                                              "pergunta", "texto"]:
                rows_to_delete.append(i)

        if len(rows_to_delete) > 0:
            df_questions.drop(rows_to_delete, inplace=True)

        # Make sure the whole DF is of type string.
        df_questions["question_no"] = df_questions["question_no"].apply(clean_option_no)
        df_questions["question"] = df_questions["question"].apply(clean_option_no)
        df_questions["options"] = df_questions["options"].apply(clean_option_no)

        if len(df_questions) == 0:
            continue

        questions = []
        for idx in range(len(df_questions)):
            o = df_questions.options.iloc[idx]
            if type(o) is str:
                options = o.split("/")
            else:
                options = []
            question = Question(question_no=str(df_questions.question_no.iloc[idx]), question_intro="blah",
                                question_text=str(df_questions.question.iloc[idx]),
                                options=options, source_page=0)
            questions.append(question)

        language = "en"
        try:
            language = detect(" ".join(df_questions["question"]))
        except:
            print("Error identifying language in Excel file")
            traceback.print_exc()
            traceback.print_stack()

        instrument = Instrument(
            file_id=file.file_id,
            instrument_id=file.file_id + "_" + str(sheet_idx),
            file_name=file.file_name,
            instrument_name=file.file_name + " / " + sheet_name,
            file_type=file.file_type,
            file_section=sheet_name,
            language=language,
            questions=questions
        )

        instruments.append(instrument)

    return instruments
