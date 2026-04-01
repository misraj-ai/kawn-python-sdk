from ..client import Client
from ..async_client import AsyncClient

class BaseService:
    """Base synchronous service."""
    def __init__(self, client: Client):
        if not isinstance(client, Client):
            raise TypeError("Expected a misraj.Client instance.")
        self._client = client


class AsyncBaseService:
    """Base asynchronous service."""
    def __init__(self, client: AsyncClient):
        if not isinstance(client, AsyncClient):
            raise TypeError("Expected a misraj.AsyncClient instance.")
        self._client = client
