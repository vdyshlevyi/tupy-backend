from starlette import status


class BaseFastAPIError(Exception):
    def __init__(
        self,
        detail: str,
        status_code: int | None = None,
        errors: dict | None = None,
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.errors = errors


class FastAPIHttpError(BaseFastAPIError):
    detail = "Fast API Server Error"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    errors = None

    def __init__(
        self,
        detail: str | None = None,
        status_code: int | None = None,
        errors: dict | None = None,
    ) -> None:
        super().__init__(
            detail=detail or self.detail,
            status_code=status_code or self.status_code,
            errors=errors or self.errors,
        )
