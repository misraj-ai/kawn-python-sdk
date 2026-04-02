# misraj.ai Python SDK

The official Python client for interacting with the misraj.ai API.

## Installation

```bash
pip install misraj.ai
```

## Setup

Set your API key as an environment variable (recommended):

```bash
export MISRAJ_API_KEY="your-api-key"
```

## Architecture Usage

The `misraj.ai` SDK is designed with decoupled services. You create a core HTTP `Client` first, and pass it to whatever specific service you need. This keeps the library robust and easy to extend.

### 1. Synchronous Usage

```python
from misraj import Client
from misraj.services import EmbeddingService, OCRService

# The client automatically picks up the MISRAJ_API_KEY environment variable.
client = Client()

# Initialize our decoupled services using the core client transport
embeddings_service = EmbeddingService(client)
ocr_service = OCRService(client)

# Text Embeddings
response = embeddings_service.create(inputs="Hello, misraj.ai!")
print(response.data[0].embedding)

# Batch Embeddings
batch_response = embeddings_service.create(inputs=[
    "This is the first sentence.",
    "This is the second sentence."
])
print(batch_response.data)

# Basser OCR: Single File Processing (Supports Images and PDFs)
ocr_res = ocr_service.process_file(file_path="document.pdf")
print(ocr_res)

# Basser OCR: Batch File Processing
batch_ocr_res = ocr_service.process_batch(file_paths=[
    "document1.png",
    "document2.pdf"
])

for res in batch_ocr_res.successful_results:
    print(res)
```

### 2. Asynchronous Usage

For high-performance applications, use the `AsyncClient` and async services.

```python
import asyncio
from misraj import AsyncClient
from misraj.services import AsyncEmbeddingService, AsyncOCRService

async def main():
    # You can also pass credentials explicitly if bypassing env variables
    async with AsyncClient(api_key="your-api-key") as client:
        
        # Initialize Async services
        embed_service = AsyncEmbeddingService(client)
        ocr_service = AsyncOCRService(client)

        batch_embed_res = await embed_service.create(
            inputs=["Concurrency is fast!", "Async batching is optimal."]
        )
        print(batch_embed_res)

        # Basser OCR Async Batch Processing
        batch_ocr_res = await ocr_service.process_batch(
            file_paths=["receipt_amount.png", "invoice.pdf"]
        )
        
        for r in batch_ocr_res.successful_results:
            print(r)

if __name__ == "__main__":
    asyncio.run(main())
```

## Utilities & PDF Processing

The `OCRService` inherently supports uploading both **images** and multi-page **PDF files** directly. There is generally no need to manually convert or split your PDFs before using the OCR API.

However, if you require more granular control—such as processing individual pages, setting a specific zoom factor, or rendering files to images offline before sending them—you can use the SDK's built-in PDF helper:

```python
from misraj.utils.pdf import convert_pdf_to_images

# Processes the PDF into separate images in parallel and saves them locally
image_files = convert_pdf_to_images(
    pdf_content="report.pdf", 
    zoom=4, 
    output_folder="./processed_pages"
)
```

## Error Handling

```python
from misraj import Client
from misraj import MisrajAPIError, AuthenticationError, RateLimitError
from misraj.exceptions import ProcessingFailedError
from misraj.services import OCRService

try:
    client = Client()
    ocr = OCRService(client)
    ocr.process_file("broken_file.jpg")
except AuthenticationError as e:
    print("Invalid API Key!", e)
except RateLimitError as e:
    print("Too many requests, slow down!", e)
except ProcessingFailedError as e:
    print("OCR Processing failed on the server!", e)
except MisrajAPIError as e:
    print(f"Generic server error: {e}")
```
