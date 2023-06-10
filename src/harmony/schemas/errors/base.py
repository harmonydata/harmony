from pydantic import BaseModel


class BadRequestError(BaseModel):
    status_code = 400
    detail = "Bad request data"


class SomethingWrongError(BaseModel):
    status_code = 500
    detail = "Something went wrong"


class UnauthorizedError(BaseModel):
    status_code = 401
    message = "Unauthorized"


class ForbiddenError(BaseModel):
    status_code = 403
    message = "Forbidden"


class ConflictError(BaseModel):
    status_code = 409
    message = "Conflict"


class ResourceNotFoundError(BaseModel):
    status_code = 404
    message = "Resource not found"
