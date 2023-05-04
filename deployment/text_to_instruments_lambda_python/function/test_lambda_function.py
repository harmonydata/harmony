import logging
from aws_xray_sdk.core import xray_recorder

logger = logging.getLogger()
xray_recorder.configure(
    context_missing='LOG_ERROR'
)
xray_recorder.begin_segment('test_init')
import json
import unittest
import jsonpickle
import lambda_function
handler = lambda_function.lambda_handler
xray_recorder.end_segment()

class TestFunction(unittest.TestCase):

    def test_function(self):
        xray_recorder.begin_segment('test_function')
        event = {"body": json.dumps({
            "file_id": "d39f31718513413fbfc620c6b6135d0c",
            "file_name": "GAD-7.txt",
            "file_type": "txt",
            "content": """I feel nervous, anxious and afraid
I feel scared"""
        })}

        logger.warning('## EVENT')
        logger.warning(jsonpickle.encode(event))
        context = {'requestid': '1234'}
        result = handler(event, context)
        result_json = json.loads(result)
        self.assertEqual(1, len(result_json), "Check 1 instrument")
        xray_recorder.end_segment()


if __name__ == '__main__':
    unittest.main()
