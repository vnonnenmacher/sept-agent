import fitz  # PyMuPDF


def extract_text_from_pdf(filepath: str) -> str:
    doc = fitz.open(filepath)
    return "\n".join(page.get_text() for page in doc)
