import base64
import io

import pandas as pd


def parse_excel_to_pandas(this_file_contents: str) -> dict:
    content_type, content_string = this_file_contents.split(",")
    excel_as_byte_array = base64.b64decode(content_string)
    xls_with_all_sheets = pd.ExcelFile(io.BytesIO(excel_as_byte_array))

    response = {}
    for sheet_name in xls_with_all_sheets.sheet_names:
        df = pd.read_excel(io.BytesIO(excel_as_byte_array), sheet_name=sheet_name, header=None)
        response[sheet_name] = df

    return response
