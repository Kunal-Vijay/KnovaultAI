class TextParser:
    def parse(self, file_content: bytes) -> str:
        # Simple parser for plain text. Decode assuming UTF-8.
        try:
            return file_content.decode("utf-8")
        except UnicodeDecodeError:
            return file_content.decode("latin-1") # Fallback for other encodings

class MarkdownParser(TextParser):
    # Markdown is essentially text, so can reuse TextParser for now.
    pass

class DocxParser:
    # Placeholder for DOCX parser. Requires a library like python-docx.
    def parse(self, file_content: bytes) -> str:
        return "Parsed content from DOCX (placeholder)"

class PdfParser:
    # Placeholder for PDF parser. Requires a library like pypdf.
    def parse(self, file_content: bytes) -> str:
        return "Parsed content from PDF (placeholder)"

def get_parser(mime_type: str):
    if "text/plain" in mime_type or "text/markdown" in mime_type:
        return TextParser()
    elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in mime_type:
        return DocxParser()
    elif "application/pdf" in mime_type:
        return PdfParser()
    else:
        raise ValueError(f"Unsupported MIME type: {mime_type}")

