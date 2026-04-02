import asyncio
import os
from typing import Union, List, Optional
from .base import BaseService, AsyncBaseService
from ..client import MisrajClient, AsyncMisrajClient
from ..types.embedding import EmbeddingRequest, EmbeddingResponse
from ..configs.constant import MAX_EMBEDDING_BATCH_SIZE, EMBEDDING_MODEL
from ..exceptions import InvalidRequestError
from ..utils.logging import get_logger

logger = get_logger("[Embedding Service]")


def _validate_input(input_data: Union[str, List[str]]):
    if isinstance(input_data, list) and len(input_data) > MAX_EMBEDDING_BATCH_SIZE:
        raise InvalidRequestError(f"Embedding batch size exceeds {MAX_EMBEDDING_BATCH_SIZE}")


class EmbeddingService(BaseService):

    def create(self,
               inputs: Union[str, List[str]],
               model: Optional[str] = None,
               **kwargs) -> EmbeddingResponse:
        _validate_input(input)

        model = model if model else EMBEDDING_MODEL

        payload = EmbeddingRequest(model=model, input=inputs, **kwargs).model_dump(exclude_none=True)

        logger.info(f"Prepare the request using {model} model, if you want to use different model "
                    f"please provide the model name within the object constructor `EmbeddingService(model='embedding-v2')`")

        res = self._client.request("POST", "/v1/embeddings/embed", json=payload)

        return EmbeddingResponse(**res.json())


class AsyncEmbeddingService(AsyncBaseService):

    async def create(self,
                     inputs: Union[str, List[str]],
                     model: Optional[str] = None,
                     **kwargs) -> EmbeddingResponse:
        _validate_input(input)
        model = model if model else EMBEDDING_MODEL
        payload = EmbeddingRequest(model=model, input=inputs, **kwargs).model_dump(exclude_none=True)

        logger.info(f"Prepare the request using {model} model, if you want to use different model "
                    f"please provide the model name within the object constructor `EmbeddingService(model='embedding-v2')`")

        res = await self._client.request("POST", "/v1/embeddings/embed", json=payload)
        return EmbeddingResponse(**res.json())
