import json
import unittest
import jsonpickle
import app
handler = app.handler

class TestFunction(unittest.TestCase):

    def test_function(self):
        event = {"body": json.dumps([{
            "file_id": "d39f31718513413fbfc620c6b6135d0c",
            "file_name": "GAD-7.txt",
            "file_type": "txt",
            "content": """I feel nervous, anxious and afraid
I feel scared"""
        }])}

        context = {'requestid': '1234'}
        result = handler(event, context)
        result_json = json.loads(result)
        self.assertEqual(1, len(result_json), "Check 1 instrument")


if __name__ == '__main__':
    unittest.main()
