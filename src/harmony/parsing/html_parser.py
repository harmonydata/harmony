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

from typing import List
from harmony.schemas.requests.text import RawFile, Instrument, Question
from harmony.parsing.util import normalise_text

# Try to import BeautifulSoup, fall back to basic text extraction if not available
try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    
# Try to import lxml for better performance, fall back to html.parser
try:
    import lxml
    DEFAULT_PARSER = 'lxml'
except ImportError:
    DEFAULT_PARSER = 'html.parser'


def convert_html_to_instruments(file: RawFile) -> List[Instrument]:
    """
    Convert HTML file to Harmony instruments by extracting text content.
    
    This function parses HTML files and extracts meaningful text content,
    attempting to preserve semantic structure while removing HTML tags.
    Uses BeautifulSoup if available for better parsing, otherwise falls
    back to basic text extraction.
    
    Args:
        file (RawFile): The raw HTML file to parse
        
    Returns:
        List[Instrument]: List of instruments extracted from the HTML
    """
    
    if not file.content:
        return []
    
    # Extract text content from HTML
    if BEAUTIFULSOUP_AVAILABLE:
        text_content = _extract_text_with_beautifulsoup(file.content)
    else:
        text_content = _extract_text_basic(file.content)
    
    if not text_content.strip():
        return []
    
    # Create questions from extracted text
    questions = _extract_questions_from_text(text_content)
    
    if not questions:
        return []
    
    # Create instrument
    instrument = Instrument(
        file_id=file.file_id,
        instrument_name=file.file_name or "HTML Document",
        questions=questions,
        language="en"  # Default to English, could be enhanced with language detection
    )
    
    return [instrument]


def _extract_text_with_beautifulsoup(html_content: str) -> str:
    """
    Extract text content from HTML using BeautifulSoup.
    
    This provides better text extraction by:
    - Removing script and style tags
    - Preserving semantic structure
    - Handling HTML entities properly
    
    Args:
        html_content (str): Raw HTML content
        
    Returns:
        str: Extracted text content
    """
    try:
        soup = BeautifulSoup(html_content, DEFAULT_PARSER)
        
        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        # Fall back to basic extraction if BeautifulSoup fails
        return _extract_text_basic(html_content)


def _extract_text_basic(html_content: str) -> str:
    """
    Basic text extraction from HTML without external dependencies.
    
    This is a fallback method that uses simple string operations
    to remove HTML tags when BeautifulSoup is not available.
    
    Args:
        html_content (str): Raw HTML content
        
    Returns:
        str: Extracted text content
    """
    import re
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html_content)
    
    # Handle common HTML entities
    html_entities = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&apos;': "'",
        '&nbsp;': ' '
    }
    
    for entity, replacement in html_entities.items():
        text = text.replace(entity, replacement)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def _extract_questions_from_text(text: str) -> List[Question]:
    """
    Extract potential questions from text content.
    
    This function looks for question-like patterns in the text and
    creates Question objects from them. It uses heuristics to identify
    sentences that might be questionnaire items.
    
    Args:
        text (str): Extracted text content
        
    Returns:
        List[Question]: List of identified questions
    """
    questions = []
    
    # Normalize the text
    normalized_text = normalise_text(text)
    
    # Split into sentences/lines for potential questions
    # Use multiple delimiters to split the text
    import re
    sentences = re.split(r'[.!?\n\r]+', normalized_text)
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        
        # Skip very short or empty sentences
        if len(sentence) < 10:
            continue
            
        # Skip sentences that are likely not questions
        if _is_likely_question(sentence):
            question = Question(
                question_no=str(i + 1),
                question_intro="",
                question_text=sentence,
                options=None,
                source_page=1
            )
            questions.append(question)
    
    return questions


def _is_likely_question(text: str) -> bool:
    """
    Determine if a text segment is likely to be a questionnaire item.
    
    Uses heuristics to identify potential questionnaire items:
    - Contains question words or patterns
    - Has appropriate length
    - Doesn't look like navigation or metadata
    
    Args:
        text (str): Text segment to evaluate
        
    Returns:
        bool: True if the text is likely a question
    """
    text_lower = text.lower()
    
    # Skip navigation and common non-question patterns
    skip_patterns = [
        'click here', 'read more', 'continue', 'next', 'previous',
        'home', 'about', 'contact', 'privacy', 'terms',
        'copyright', 'all rights reserved', 'menu', 'navigation'
    ]
    
    for pattern in skip_patterns:
        if pattern in text_lower:
            return False
    
    # Look for question indicators
    question_indicators = [
        'how', 'what', 'when', 'where', 'why', 'who', 'which',
        'do you', 'are you', 'have you', 'would you', 'could you',
        'please', 'rate', 'scale', 'agree', 'disagree', 'often',
        'never', 'sometimes', 'always', 'feel', 'think', 'believe'
    ]
    
    # Check for question indicators
    for indicator in question_indicators:
        if indicator in text_lower:
            return True
    
    # Check if it ends with a question mark
    if text.strip().endswith('?'):
        return True
    
    # Check length - typical questionnaire items are of reasonable length
    if 20 <= len(text) <= 200:
        # Additional heuristics for questionnaire-like content
        if any(word in text_lower for word in ['you', 'your', 'i', 'my']):
            return True
    
    return False
