import fitz  # PyMuPDF
from typing import List, Union

def convert_pdf_to_images(pdf_content: Union[bytes, str], zoom: int = 4) -> List[bytes]:
    """
    Converts a PDF file (path or raw bytes) into a list of PNG image bytes using PyMuPDF.
    Each item in the list represents a single page of the PDF rendered as an image.
    """
    images_bytes = []
    
    if isinstance(pdf_content, str):
        doc = fitz.open(pdf_content)
    else:
        # Provide the stream type as 'pdf' to parse from bytes
        doc = fitz.open("pdf", pdf_content)

    matrix = fitz.Matrix(zoom, zoom)

    try:
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=matrix)
            
            # Returns the raw PNG bytes of the generated image without needing to write to disk.
            images_bytes.append(pix.tobytes("png"))
    finally:
        doc.close()
        
    return images_bytes
