"""
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

"""

from typing import List, Optional


def strip_prefixes(question: str, prefixes: Optional[List[str]] = None) -> str:
    """
    Strips specified prefixes from a question string if they are present.

    Args:
        question (str): The question string from which prefixes need to be removed.
        prefixes (Optional[List[str]]): A list of prefixes to remove from the question.
                                        If not provided, a default set of common prefixes is used.

    Returns:
        str: The question string with the prefix removed, if a match is found;
             otherwise, the original question.

    Example:
        question = "Have you ever traveled abroad?"
        result = strip_prefixes(question)
        # result -> "traveled abroad?"
    """
    default_prefixes = [
        "Have you ever",
        "Did you ever",
        "Do you",
        "Is it true that",
        "Would you say",
        "Can you",
        "Are you aware that",
        "Do you think",
    ]
    prefixes = prefixes or default_prefixes

    for prefix in prefixes:
        if question.lower().startswith(prefix.lower()):
            return question[len(prefix) :].strip()
    return question
