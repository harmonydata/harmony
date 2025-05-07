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

import base64
import hashlib
import requests
import ssl
import urllib.parse
import uuid
from datetime import datetime, timedelta
from harmony.parsing.wrapper_all_parsers import convert_files_to_instruments
from harmony.schemas.errors.base import BadRequestError, ForbiddenError, ConflictError, SomethingWrongError
from harmony.schemas.requests.text import RawFile, Instrument, FileType
from pathlib import Path
from requests.adapters import HTTPAdapter
from typing import List, Dict

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
DOWNLOAD_TIMEOUT = 30  # seconds
MAX_REDIRECTS = 5
ALLOWED_SCHEMES = {'https'}
RATE_LIMIT_REQUESTS = 60  # requests per min
RATE_LIMIT_WINDOW = 60  # seconds

MIME_TO_FILE_TYPE = {
    'application/pdf': FileType.pdf,
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': FileType.xlsx,
    'text/plain': FileType.txt,
    'text/csv': FileType.csv,
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': FileType.docx
}

EXT_TO_FILE_TYPE = {
    '.pdf': FileType.pdf,
    '.xlsx': FileType.xlsx,
    '.txt': FileType.txt,
    '.csv': FileType.csv,
    '.docx': FileType.docx
}


class URLDownloader:
    def __init__(self):
        self.rate_limit_storage: Dict[str, List[datetime]] = {}
        self.session = requests.Session()
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.session.verify = True

    def _check_rate_limit(self, domain: str) -> None:
        now = datetime.now()
        if domain not in self.rate_limit_storage:
            self.rate_limit_storage[domain] = []

        self.rate_limit_storage[domain] = [
            ts for ts in self.rate_limit_storage[domain]
            if ts > now - timedelta(seconds=RATE_LIMIT_WINDOW)
        ]

        if len(self.rate_limit_storage[domain]) >= RATE_LIMIT_REQUESTS:
            raise ConflictError("Rate limit exceeded")

        self.rate_limit_storage[domain].append(now)

    def _validate_url(self, url: str) -> None:
        try:
            parsed = urllib.parse.urlparse(url)

            if parsed.scheme not in ALLOWED_SCHEMES:
                raise BadRequestError(f"URL must use HTTPS")

            if not parsed.netloc or '.' not in parsed.netloc:
                raise BadRequestError("Invalid domain")

            if '..' in parsed.path or '//' in parsed.path:
                raise ForbiddenError("Path traversal detected")

            if parsed.fragment:
                raise BadRequestError("URL fragments not supported")

            blocked_domains = {'localhost', '127.0.0.1', '0.0.0.0'}
            if parsed.netloc in blocked_domains:
                raise ForbiddenError("Access to internal domains blocked")

        except Exception as e:
            raise BadRequestError(f"Invalid URL: {str(e)}")

    def _validate_ssl(self, response: requests.Response) -> None:
        cert = response.raw.connection.sock.getpeercert()
        if not cert:
            raise ForbiddenError("Invalid SSL certificate")

        not_after = ssl.cert_time_to_seconds(cert['notAfter'])
        if datetime.fromtimestamp(not_after) < datetime.now():
            raise ForbiddenError("Expired SSL certificate")

    def _check_legal_headers(self, response: requests.Response) -> None:
        if response.headers.get('X-Robots-Tag', '').lower() == 'noindex':
            raise ForbiddenError("Access not allowed by robots directive")

        if 'X-Copyright' in response.headers:
            raise ForbiddenError("Content is copyright protected")

        if 'X-Terms-Of-Service' in response.headers:
            raise ForbiddenError("Terms of service acceptance required")

    def _validate_content_type(self, url: str, content_type: str) -> FileType:
        try:
            content_type = content_type.split(';')[0].lower()

            if content_type in MIME_TO_FILE_TYPE:
                return MIME_TO_FILE_TYPE[content_type]

            ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
            if ext in EXT_TO_FILE_TYPE:
                return EXT_TO_FILE_TYPE[ext]

            raise BadRequestError(f"Unsupported file type: {content_type}")
        except BadRequestError:
            raise
        except Exception as e:
            raise BadRequestError(f"Error validating content type: {str(e)}")

    def download(self, url: str) -> RawFile:
        try:
            self._validate_url(url)
            domain = urllib.parse.urlparse(url).netloc
            self._check_rate_limit(domain)

            response = self.session.get(
                url,
                timeout=DOWNLOAD_TIMEOUT,
                stream=True,
                verify=True,
                allow_redirects=True,
                headers={
                    'User-Agent': 'HarmonyBot/1.0 (+https://harmonydata.ac.uk)',
                    'Accept': ', '.join(MIME_TO_FILE_TYPE.keys())
                }
            )
            response.raise_for_status()

            self._validate_ssl(response)
            self._check_legal_headers(response)

            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_FILE_SIZE:
                raise ForbiddenError(f"File too large: {content_length} bytes (max {MAX_FILE_SIZE})")

            file_type = self._validate_content_type(url, response.headers.get('content-type', ''))

            hasher = hashlib.sha256()
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                hasher.update(chunk)
                content += chunk

            if file_type in [FileType.pdf, FileType.xlsx, FileType.docx]:
                content_str = f"data:{response.headers['content-type']};base64," + base64.b64encode(content).decode(
                    'ascii')
            else:
                content_str = content.decode('utf-8')

            return RawFile(
                file_id=str(uuid.uuid4()),
                file_name=Path(urllib.parse.urlparse(url).path).name or "downloaded_file",
                file_type=file_type,
                content=content_str,
                metadata={
                    'content_hash': hasher.hexdigest(),
                    'download_timestamp': datetime.now().isoformat(),
                    'source_url': url
                }
            )

        except (BadRequestError, ForbiddenError, ConflictError):
            raise
        except requests.Timeout:
            raise SomethingWrongError("Download timeout")
        except requests.TooManyRedirects:
            raise ForbiddenError("Too many redirects")
        except requests.RequestException as e:
            if e.response is not None:
                if e.response.status_code == 401:
                    raise ForbiddenError("Resource requires authentication")
                elif e.response.status_code == 403:
                    raise ForbiddenError("Access forbidden")
                elif e.response.status_code == 429:
                    raise ConflictError("Rate limit exceeded")
            raise SomethingWrongError(f"Download error: {str(e)}")
        except Exception as e:
            raise SomethingWrongError(f"Unexpected error: {str(e)}")


def load_instruments_from_url(url: str) -> List[Instrument]:
    downloader = URLDownloader()
    raw_file = downloader.download(url)
    return convert_files_to_instruments([raw_file])
