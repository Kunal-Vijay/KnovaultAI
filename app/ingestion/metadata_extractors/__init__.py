class BasicMetadataExtractor:
    def extract(self, document_content: bytes, filename: str, mime_type: str) -> dict:
        # Placeholder for metadata extraction. Can be extended later.
        metadata = {
            "source": filename,
            "page_number": None, # To be determined by parser
            "section": None, # To be determined by parser
        }
        if "text/plain" in mime_type or "text/markdown" in mime_type:
            metadata["num_pages"] = 1 # Assuming single page for plain text/markdown
        # More sophisticated extraction for PDF/DOCX would go here
        return metadata

def get_metadata_extractor():
    return BasicMetadataExtractor()
