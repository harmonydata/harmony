import json
from pydantic import parse_obj_as
import logging
from harmony import convert_file_to_instruments
from harmony.schemas.enums.file_types import FileType
from harmony.schemas.requests.text import RawFile
from harmony.schemas.responses.text import InstrumentList
import requests
import jsonpickle
import os
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    file = parse_obj_as(RawFile, json.loads(event["body"]))

    print ("file type", file.file_type, " AAAA ", file.file_type == FileType.pdf)

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
        print  ("Response from Tika [" + response.text + "]")
        file.text_content = response.text

    instruments = convert_file_to_instruments(file)
    instruments_list = InstrumentList(__root__=instruments)

    return instruments_list.json()
