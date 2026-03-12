'''
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

'''

import os
import re
import traceback
from typing import List, Optional, Dict, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langdetect import detect

from harmony.schemas.requests.text import RawFile, Instrument, Question
from harmony.schemas.enums.file_types import FileType


def extract_form_id_from_url(url: str) -> Optional[str]:
    """
    Extract Google Forms form ID from various URL formats.

    Supports:
    - https://docs.google.com/forms/d/FORM_ID/edit
    - https://docs.google.com/forms/d/e/FORM_ID/viewform
    - Direct form ID

    Args:
        url: Google Forms URL or form ID

    Returns:
        Form ID string or None if not found

    Examples:
        >>> extract_form_id_from_url("https://docs.google.com/forms/d/1FAIpQLSc.../viewform")
        '1FAIpQLSc...'
        >>> extract_form_id_from_url("1FAIpQLSc...")
        '1FAIpQLSc...'
    """
    # Pattern for extracting form ID from Google Forms URLs
    # Matches: /d/FORM_ID or /d/e/FORM_ID
    pattern = r'docs\.google\.com/forms/d/(?:e/)?([a-zA-Z0-9_-]+)'

    match = re.search(pattern, url)
    if match:
        return match.group(1)

    # If no match and input looks like a form ID (alphanumeric, hyphens, underscores)
    if re.match(r'^[a-zA-Z0-9_-]+$', url):
        return url

    return None


def fetch_form_structure(form_id: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch form structure from Google Forms API using API key authentication.

    Args:
        form_id: Google Forms form ID
        api_key: Google API key (if None, reads from GOOGLE_FORMS_API_KEY env var)

    Returns:
        Dictionary containing form structure from API

    Raises:
        ValueError: If API key is not provided
        HttpError: If API request fails
    """
    if api_key is None:
        api_key = os.environ.get('GOOGLE_FORMS_API_KEY')

    if not api_key:
        raise ValueError(
            "Google Forms API key not found. "
            "Please set GOOGLE_FORMS_API_KEY environment variable or provide api_key parameter."
        )

    try:
        # Build service with API key (no OAuth required)
        service = build('forms', 'v1', developerKey=api_key)

        # Fetch form
        result = service.forms().get(formId=form_id).execute()
        return result

    except HttpError as error:
        error_details = error.error_details if hasattr(error, 'error_details') else str(error)
        print(f"Error fetching Google Form {form_id}: {error_details}")
        traceback.print_exc()
        raise


def parse_question_item(item: Dict[str, Any], question_number: int) -> Optional[Question]:
    """
    Parse a single question item from Google Forms API response.

    Args:
        item: Dictionary containing question item data
        question_number: Sequential number for the question

    Returns:
        Question object or None if item is not a question
    """
    # Skip if not a question item
    if 'questionItem' not in item:
        return None

    question_item = item['questionItem']
    question_data = question_item.get('question', {})

    # Extract question text from title
    question_text = item.get('title', '').strip()
    if not question_text:
        return None

    # Extract description as intro if available
    question_intro = item.get('description', '')

    # Extract options based on question type
    options = []

    # Multiple choice, checkbox, or dropdown
    if 'choiceQuestion' in question_data:
        choice_question = question_data['choiceQuestion']
        choice_options = choice_question.get('options', [])
        options = [opt.get('value', '') for opt in choice_options if opt.get('value')]

    # Linear scale (rating scale)
    elif 'scaleQuestion' in question_data:
        scale_question = question_data['scaleQuestion']
        low = scale_question.get('low', 1)
        high = scale_question.get('high', 5)
        low_label = scale_question.get('lowLabel', '')
        high_label = scale_question.get('highLabel', '')

        # Create options as range
        options = [str(i) for i in range(low, high + 1)]

        # Add labels if present
        if low_label or high_label:
            if question_intro:
                question_intro += f" [{low_label} - {high_label}]"
            else:
                question_intro = f"[{low_label} - {high_label}]"

    # Grid question (matrix)
    elif 'rowQuestion' in question_data:
        row_question = question_data['rowQuestion']
        # For grid questions, title is the column header
        # We'll extract row options as answer choices
        if 'rows' in row_question:
            row_items = row_question.get('rows', [])
            options = [row.get('title', '') for row in row_items if row.get('title')]

    # Text question, file upload, date/time - no options
    # These will have empty options list

    return Question(
        question_no=str(question_number),
        question_intro=question_intro,
        question_text=question_text,
        options=options,
        source_page=0
    )


def parse_google_form_structure(form_data: Dict[str, Any]) -> Instrument:
    """
    Parse complete Google Form structure into Harmony Instrument.

    Args:
        form_data: Complete form structure from Google Forms API

    Returns:
        Instrument object with all questions and metadata
    """
    # Extract form metadata
    info = form_data.get('info', {})
    form_title = info.get('title', 'Untitled Google Form')
    form_description = info.get('description', '')

    # Extract document ID
    form_id = form_data.get('formId', '')

    # Parse all question items
    questions = []
    items = form_data.get('items', [])

    question_counter = 0
    for item in items:
        question = parse_question_item(item, question_counter + 1)
        if question:
            questions.append(question)
            question_counter += 1

    # Detect language from questions
    language = "en"
    if questions:
        try:
            # Combine first few questions for language detection
            sample_text = " ".join([q.question_text for q in questions[:5] if q.question_text])
            if sample_text:
                language = detect(sample_text)
        except:
            print("Error identifying language in Google Form")
            traceback.print_exc()
            language = "en"

    # Create metadata dictionary
    metadata = {
        'form_id': form_id,
        'title': form_title,
        'description': form_description,
        'source': 'google_forms',
        'document_title': info.get('documentTitle', ''),
    }

    # Create instrument
    instrument = Instrument(
        file_id=form_id,
        instrument_id=form_id,
        instrument_name=form_title,
        file_name=f"{form_title}.google_forms",
        file_type=FileType.google_forms,
        file_section="",
        language=language,
        questions=questions,
        metadata=metadata
    )

    return instrument


def convert_google_forms_to_instruments(file: RawFile) -> List[Instrument]:
    """
    Convert Google Forms URL or form ID to Harmony instruments.

    This function handles two scenarios:
    1. content contains a Google Forms URL or form ID
    2. content contains pre-fetched JSON structure from Google Forms API

    Args:
        file: RawFile object with content containing:
              - Google Forms URL (e.g., https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform)
              - Form ID directly
              - JSON structure from Forms API (for testing)

    Returns:
        List containing single Instrument object with parsed questions

    Raises:
        ValueError: If form ID cannot be extracted or API key is missing
        HttpError: If API request fails

    Examples:
        >>> file = RawFile(
        ...     file_name="Survey.google_forms",
        ...     file_type=FileType.google_forms,
        ...     content="https://docs.google.com/forms/d/e/1FAIpQLSc.../viewform"
        ... )
        >>> instruments = convert_google_forms_to_instruments(file)
    """
    try:
        content = file.content.strip()

        # Check if content is JSON (pre-fetched structure for testing)
        if content.startswith('{'):
            import json
            form_data = json.loads(content)
        else:
            # Extract form ID from URL or direct ID
            form_id = extract_form_id_from_url(content)
            if not form_id:
                raise ValueError(
                    f"Could not extract form ID from: {content}. "
                    "Please provide a valid Google Forms URL or form ID."
                )

            # Fetch form structure from API
            form_data = fetch_form_structure(form_id)

        # Parse form structure
        instrument = parse_google_form_structure(form_data)

        # Update file_name if it was default
        if file.file_name == "Untitled file" or not file.file_name:
            instrument.file_name = instrument.instrument_name
        else:
            instrument.file_name = file.file_name

        return [instrument]

    except Exception as e:
        print(f"Error converting Google Form: {str(e)}")
        traceback.print_exc()
        raise
