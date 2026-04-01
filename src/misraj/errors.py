class MisrajAPIError(Exception):
    """Base exception for all misraj API errors."""
    def __init__(self, message: str, status_code: int = None, body: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body

class AuthenticationError(MisrajAPIError):
    """Raised when the API returns a 401 Unauthorized error."""
    pass

class RateLimitError(MisrajAPIError):
    """Raised when the API returns a 429 Too Many Requests error."""
    pass

class APIConnectionError(MisrajAPIError):
    """Raised when the client cannot connect to the API (e.g., timeout, network issue)."""
    pass

class ValidationError(MisrajAPIError):
    """Raised when the payload is invalid."""
    pass
