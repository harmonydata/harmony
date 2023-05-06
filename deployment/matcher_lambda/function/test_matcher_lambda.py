import json
import unittest

import lambda_function

handler = lambda_function.lambda_handler


class TestMatcherLambda(unittest.TestCase):

    def test_matcher_gad_7_en_pt(self):
        event = {"body": json.dumps({
            "instruments": [
                {
                    "file_id": "fd60a9a64b1b4078a68f4bc06f20253c",
                    "instrument_id": "7829ba96f48e4848abd97884911b6795",
                    "instrument_name": "GAD-7 English",
                    "file_name": "GAD-7 EN.pdf",
                    "file_type": "pdf",
                    "file_section": "GAD-7 English",
                    "language": "en",
                    "questions": [
                        {
                            "question_no": "1",
                            "question_intro": "Over the last two weeks, how often have you been bothered by the following problems?",
                            "question_text": "Feeling nervous, anxious, or on edge",
                            "options": [
                                "Not at all",
                                "Several days",
                                "More than half the days",
                                "Nearly every day"
                            ],
                            "source_page": 0
                        },
                        {
                            "question_no": "2",
                            "question_intro": "Over the last two weeks, how often have you been bothered by the following problems?",
                            "question_text": "Not being able to stop or control worrying",
                            "options": [
                                "Not at all",
                                "Several days",
                                "More than half the days",
                                "Nearly every day"
                            ],
                            "source_page": 0
                        }
                    ]
                },
                {
                    "file_id": "fd60a9a64b1b4078a68f4bc06f20253c",
                    "instrument_id": "7829ba96f48e4848abd97884911b6795",
                    "instrument_name": "GAD-7 Portuguese",
                    "file_name": "GAD-7 PT.pdf",
                    "file_type": "pdf",
                    "file_section": "GAD-7 Portuguese",
                    "language": "en",
                    "questions": [
                        {
                            "question_no": "1",
                            "question_intro": "Durante as últimas 2 semanas, com que freqüência você foi incomodado/a pelos problemas abaixo?",
                            "question_text": "Sentir-se nervoso/a, ansioso/a ou muito tenso/a",
                            "options": [
                                "Nenhuma vez",
                                "Vários dias",
                                "Mais da metade dos dias",
                                "Quase todos os dias"
                            ],
                            "source_page": 0
                        },
                        {
                            "question_no": "2",
                            "question_intro": "Durante as últimas 2 semanas, com que freqüência você foi incomodado/a pelos problemas abaixo?",
                            "question_text": " Não ser capaz de impedir ou de controlar as preocupações",
                            "options": [
                                "Nenhuma vez",
                                "Vários dias",
                                "Mais da metade dos dias",
                                "Quase todos os dias"
                            ],
                            "source_page": 0
                        }
                    ]
                }
            ],
            "query": "anxiety",
            "parameters": {
                "framework": "huggingface",
                "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            }
        })}

        context = {'requestid': '1234'}
        result = handler(event, context)
        result_json = json.loads(result)
        print(result_json)
        self.assertEqual(4, len(result_json["questions"]), "Check number of questions")
        self.assertLess(0.999, result_json["matches"][0][0], "Check ones on diagonal")
        self.assertLess(0.999, result_json["matches"][1][1], "Check ones on diagonal")

        # Try again and check cache is working
        result = handler(event, context)
        result_json = json.loads(result)
        print(result_json)
        self.assertEqual(4, len(result_json["questions"]), "Check number of questions")
        self.assertLess(0.999, result_json["matches"][0][0], "Check ones on diagonal")
        self.assertLess(0.999, result_json["matches"][1][1], "Check ones on diagonal")

if __name__ == '__main__':
    unittest.main()
