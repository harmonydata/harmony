import json
import logging
import os

import boto3
import jsonpickle
from aws_xray_sdk.core import patch_all
from pydantic import parse_obj_as

from harmony import convert_text_to_instruments
from harmony.schemas.requests.text import RawFile
from harmony.schemas.responses.text import InstrumentList

logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()

client = boto3.client('lambda')
client.get_account_settings()

def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES\r' + jsonpickle.encode(dict(**os.environ)))
    logger.info('## EVENT\r' + jsonpickle.encode(event))
    logger.info('## CONTEXT\r' + jsonpickle.encode(context))
    file = parse_obj_as(RawFile, json.loads(event["body"]))

    instruments = convert_text_to_instruments(file)
    instruments_list = InstrumentList(__root__=instruments)

    return instruments_list.json()
