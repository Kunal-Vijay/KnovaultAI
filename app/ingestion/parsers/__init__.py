import io

from pypdf import PdfReader
from docx import Document as DocxDocument


class TextParser:
    def parse(self, file_content: bytes) -> str:
        try:
            return file_content.decode("utf-8")
        except UnicodeDecodeError:
            return file_content.decode("latin-1")


class MarkdownParser(TextParser):
    pass


class DocxParser:
    def parse(self, file_content: bytes) -> str:
        doc = DocxDocument(io.BytesIO(file_content))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)


class PdfParser:
    def parse(self, file_content: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_content))
        pages: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                pages.append(text)
        return "\n\n".join(pages)


def get_parser(mime_type: str):
    if "text/plain" in mime_type or "text/markdown" in mime_type:
        return TextParser()
    if "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in mime_type:
        return DocxParser()
    if "application/pdf" in mime_type:
        return PdfParser()
    raise ValueError(f"Unsupported MIME type: {mime_type}")
