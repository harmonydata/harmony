import base64
import json
import logging
import os
from typing import List

import jsonpickle
import requests
from pydantic import parse_obj_as

from harmony import convert_files_to_instruments
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile
from harmony.schemas.responses.text import InstrumentList

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_to_instruments_cache = {}


def handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    files = parse_obj_as(List[RawFile], json.loads(event["body"]))

    if len(files) > 1:
        return ''''{"Error":"Please send only one file to Lambda function."}'''

    # Check in cache if this file has already been converted to an instrument.
    for file in files:
        file.file_id = str(hash(file.content))
        if file.file_id in file_to_instruments_cache:
            return InstrumentList(__root__=[file_to_instruments_cache[file.file_id]])

    for file in files:
        if file.file_type == FileType.pdf:
            # We parse PDF using a call to another Lambda
            headers = {
                'Content-Type': 'application/pdf'
            }
            pdf_bytes = base64.b64decode(file.content)
            response = requests.post("https://vewj7t7cpafppz6jf75im4lfwm0vrgkb.lambda-url.eu-west-2.on.aws",
                                     headers=headers,
                                     data=pdf_bytes
                                     )
            print("Response from Tika [" + response.text + "]")
            file.text_content = response.text

    instruments = convert_files_to_instruments(files)

    # Store in cache
    for instrument in instruments:
        file_to_instruments_cache[instrument.file_id] = instrument

    instruments_list = InstrumentList(__root__=instruments)

    return instruments_list.json()
