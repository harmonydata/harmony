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

class BaseException(Exception):
    status_code = 500
    message = "Something went wrong"


class ResourceNotFoundException(Exception):
    def __init__(self, message: str = None):
        self.status_code = 404
        if not message:
            message = "Resource not found"
        self.message = message
        super().__init__(message)


class FailedCreatingResourceException(Exception):
    def __init__(self, message: str = None):
        self.status_code = 400
        if not message:
            message = "Failed when creating resource."
        self.message = message
        super().__init__(message)


class ConflictException(Exception):
    def __init__(self, message: str = None):
        self.status_code = 409
        if not message:
            message = "Conflict"
        self.message = message
        super().__init__(message)


class ForbiddenException(Exception):
    def __init__(self, message: str = None):
        self.status_code = 403
        if not message:
            message = "Forbidden"
        self.message = message
        super().__init__(message)


class UnauthorizedException(Exception):
    def __init__(self, message: str = None):
        self.status_code = 401
        if not message:
            message = "Unauthorized"
        self.message = message
        super().__init__(message)


class LimitExceeded(Exception):
    def __init__(self, message: str = None):
        self.status_code = 401
        if not message:
            message = "Too many requests, try again later."
        self.message = message
        super().__init__(message)
