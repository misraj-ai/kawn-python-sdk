import os
import httpx
from typing import Any, Optional
from .errors import AuthenticationError, RateLimitError, APIConnectionError, MisrajAPIError

class AsyncClient:
    """
    Asynchronous HTTP Client for the misraj.ai SDK.
    Used purely as an async transport wrapper.
    """
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "https://api.misraj.ai/v1", 
        timeout: float = 60.0,
        max_retries: int = 2
    ):
        self.api_key = api_key or os.getenv("MISRAJ_API_KEY")
        if not self.api_key:
            raise AuthenticationError("API key must be provided explicitly or set via MISRAJ_API_KEY environment variable.")

        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "misraj-python/0.1.0"
            },
            timeout=httpx.Timeout(timeout)
        )

    async def request(self, method: str, path: str, **kwargs: Any) -> Any:
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(method, path, **kwargs)
                self._handle_response(response)
                return response.json()
            except httpx.RequestError as e:
                last_error = e
            except MisrajAPIError as e:
                # Retry on rate limits or 500+ errors
                if e.status_code and (e.status_code == 429 or e.status_code >= 500):
                    last_error = e
                else:
                    raise e
                    
        message = str(last_error) if last_error else "Unknown async error occurred."
        raise APIConnectionError(f"Failed after {self.max_retries + 1} attempts. Reason: {message}")

    def _handle_response(self, response: httpx.Response):
        if response.is_success:
            return
            
        status = response.status_code
        try:
            body = response.json()
            message = body.get("error", {}).get("message", response.text)
        except ValueError:
            body = response.text
            message = response.text
            
        if status == 401:
            raise AuthenticationError(f"Authentication failed: {message}", status_code=status, body=body)
        elif status == 429:
            raise RateLimitError(f"Rate limit exceeded: {message}", status_code=status, body=body)
        else:
            raise MisrajAPIError(f"API Error ({status}): {message}", status_code=status, body=body)

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
