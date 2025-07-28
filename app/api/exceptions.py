from starlette import status

from app.exceptions import FastAPIHttpError


class ObjectNotFoundError(FastAPIHttpError):
    """Exception raised when object does not exist."""

    detail = "Object was not found error."
    status_code = status.HTTP_404_NOT_FOUND


class APIValidationError(FastAPIHttpError):
    """Base API validation error for inheritance."""

    detail = "API validation error."
    status_code = status.HTTP_400_BAD_REQUEST


class UnauthorizedError(APIValidationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Unauthorized."


class ForbiddenError(APIValidationError):
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, reason: str) -> None:
        super().__init__(detail=f"Forbidden by {reason}.")


class ConflictError(FastAPIHttpError):
    status_code = status.HTTP_409_CONFLICT
