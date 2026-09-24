from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(file_bytes: bytes) -> str:
    pdf = PdfReader(BytesIO(file_bytes))

    pages = []

    for page in pdf.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n\n".join(pages)

def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200,
) -> list[str]:
    
    chunks = []
    
    start = 0
    
    while start <len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        
        if(chunk):
            chunks.append(chunk)
        
        start += chunk_size - overlap
    
    return chunks