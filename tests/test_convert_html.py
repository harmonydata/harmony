import unittest
from harmony import load_instruments_from_local_file
from harmony.schemas.requests.text import Instrument
import tempfile
import os


class TestLoadInstrumentsFromLocalFile(unittest.TestCase):
    def setUp(self):
        """Set up temporary files for testing."""
        # English HTML content
        self.html_content_english = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>GAD-7 Form</title>
        </head>
        <body>
          <div class="title">GAD-7</div>
          <h2>Over the last 2 weeks, how often have you been bothered by the following problems?</h2>
          <table>
            <thead>
              <tr>
                <th class="question">Question</th>
                <th>Not at all<br>(0)</th>
                <th>Several days<br>(1)</th>
                <th>More than half the days<br>(2)</th>
                <th>Nearly every day<br>(3)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="question">1. Feeling nervous, anxious, or on edge</td>
                <td><input type="radio" name="q1" value="0"></td>
                <td><input type="radio" name="q1" value="1"></td>
                <td><input type="radio" name="q1" value="2"></td>
                <td><input type="radio" name="q1" value="3"></td>
              </tr>
            </tbody>
          </table>
        </body>
        </html>
        """
        # Chinese HTML content
        self.html_content_chinese = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
          <meta charset="UTF-8">
          <title>广泛性焦虑症量表(GAD-7)</title>
        </head>
        <body>
          <h1>广泛性焦虑症量表(GAD-7)</h1>
          <p><strong>在过去两个星期，有多少时候您受到以下问题所困扰？</strong></p>
          <table>
            <thead>
              <tr>
                <th>问题</th>
                <th>完全没有<br>(0)</th>
                <th>几天<br>(1)</th>
                <th>一半以上天数<br>(2)</th>
                <th>几乎每天<br>(3)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="question">1. 感觉紧张、焦虑或不安</td>
                <td><input type="radio" name="q1" value="0"></td>
                <td><input type="radio" name="q1" value="1"></td>
                <td><input type="radio" name="q1" value="2"></td>
                <td><input type="radio" name="q1" value="3"></td>
              </tr>
            </tbody>
          </table>
        </body>
        </html>
        """
        # Temporary files
        self.temp_file_english = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        self.temp_file_english.write(self.html_content_english.encode('utf-8'))
        self.temp_file_english.close()

        self.temp_file_chinese = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        self.temp_file_chinese.write(self.html_content_chinese.encode('utf-8'))
        self.temp_file_chinese.close()

    def tearDown(self):
        """Remove temporary files after tests."""
        os.unlink(self.temp_file_english.name)
        os.unlink(self.temp_file_chinese.name)

    def test_load_instruments_english_html(self):
        """Test loading instruments from an English HTML file."""
        instruments = load_instruments_from_local_file(self.temp_file_english.name)

        self.assertIsInstance(instruments, list)

        self.assertGreater(len(instruments), 0)

        instrument = instruments[0]
        self.assertIsInstance(instrument, Instrument)

        self.assertEqual(instrument.instrument_name, "GAD-7 Form")
        self.assertGreater(len(instrument.questions), 0)


    def test_load_instruments_chinese_html(self):
        """Test loading instruments from a Chinese HTML file."""
        instruments = load_instruments_from_local_file(self.temp_file_chinese.name)

        self.assertIsInstance(instruments, list)

        self.assertGreater(len(instruments), 0)

        instrument = instruments[0]
        self.assertIsInstance(instrument, Instrument)

        self.assertEqual(instrument.instrument_name, "广泛性焦虑症量表(GAD-7)")
        self.assertGreater(len(instrument.questions), 0)


if __name__ == "__main__":
    unittest.main()
