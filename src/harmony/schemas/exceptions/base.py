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
