import asyncio
import time
import json
from pathlib import Path
from typing import Union, List, Optional
from concurrent.futures import ThreadPoolExecutor

from .base import AsyncBaseService, BaseService
from ..types.ocr import OCRUploadResponse, OCRStatusResponse, OCRResult, OCRBatchResult
from ..configs.constant import POLL_INTERVAL, MAX_OCR_BATCH_SIZE, OCR_MODEL, MAX_THREAD_FOR_BATCH_REQUEST
from ..exceptions import ProcessingFailedError, InvalidRequestError


class OCRService(BaseService):

    def process_image(self,
                      file_path: Union[str, Path],
                      model: Optional[str] = None,
                      options: Optional[dict] = None) -> OCRResult:

        file_path = Path(file_path)
        data = {"model": model if model else OCR_MODEL}

        if options:
            data["options"] = json.dumps(options)

        # 1. Upload
        with open(file_path, "rb") as f:
            file = {"file": (file_path.name, f)}
            res = self._client.request("POST", "/ocr", data=data, file=file)

        file_id = OCRUploadResponse(**res.json()).fileId

        # 2. Poll
        while True:
            status_res = self._client.request("GET", f"/ocr/{file_id}/status")
            status_data = OCRStatusResponse(**status_res.json())
            if status_data.status == "completed":
                break
            elif status_data.status == "failed":
                raise ProcessingFailedError(f"OCR processing failed for file {file_id}")
            time.sleep(POLL_INTERVAL)

        # 3. Retrieve
        result_res = self._client.request("GET", f"/ocr/{file_id}/results")
        return OCRResult(**result_res.json())

    def process_batch(self,
                      file_paths: List[Union[str, Path]],
                      model: Optional[str] = None,
                      options: Optional[dict] = None) -> OCRBatchResult:

        if len(file_paths) > MAX_OCR_BATCH_SIZE:
            raise InvalidRequestError(f"Batch size exceeds {MAX_OCR_BATCH_SIZE}")

        batch_result = OCRBatchResult()
        with ThreadPoolExecutor(max_workers=min(len(file_paths), MAX_THREAD_FOR_BATCH_REQUEST)) as executor:
            future_to_path = {executor.submit(self.process_image, fp, model, options): fp for fp in file_paths}
            for future in future_to_path:
                try:
                    batch_result.successful_results.append(future.result())
                except Exception as exc:
                    batch_result.failed_files.append(str(future_to_path[future]))
        return batch_result


class AsyncOCRService(AsyncBaseService):

    async def process_image(self,
                            file_path: Union[str, Path],
                            model: Optional[str] = None,
                            options: Optional[dict] = None) -> OCRResult:
        file_path = Path(file_path)
        data = {"model": model if model else OCR_MODEL}
        if options:
            data["options"] = json.dumps(options)

        with open(file_path, "rb") as f:
            file = {"file": (file_path.name, f)}
            res = await self._client.request("POST", "/ocr", data=data, file=file)

        file_id = OCRUploadResponse(**res.json()).fileId

        while True:
            status_res = await self._client.request("GET", f"/ocr/{file_id}/status")
            status_data = OCRStatusResponse(**status_res.json())
            if status_data.status == "completed":
                break
            elif status_data.status == "failed":
                raise ProcessingFailedError(f"OCR processing failed for file {file_id}")
            await asyncio.sleep(POLL_INTERVAL)

        result_res = await self._client.request("GET", f"/ocr/{file_id}/results")
        return OCRResult(**result_res.json())

    async def process_batch(self,
                            file_paths: List[Union[str, Path]],
                            model: Optional[str] = None,
                            options: Optional[dict] = None) -> OCRBatchResult:

        if len(file_paths) > MAX_OCR_BATCH_SIZE:
            raise InvalidRequestError(f"Batch size exceeds {MAX_OCR_BATCH_SIZE}")

        tasks = [self.process_image(fp, model, options) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        batch_result = OCRBatchResult()
        for fp, result in zip(file_paths, results):
            if isinstance(result, Exception):
                batch_result.failed_files.append(str(fp))
            else:
                batch_result.successful_results.append(result)
        return batch_result
