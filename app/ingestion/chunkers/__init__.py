class BasicChunker:
    def chunk(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
        # Simple chunking by splitting text into fixed-size chunks
        chunks = []
        words = text.split()
        i = 0
        while i < len(words):
            chunk = words[i:i + chunk_size]
            chunks.append(" ".join(chunk))
            i += chunk_size - chunk_overlap
            if i < 0: # Handle cases where chunk_overlap is greater than chunk_size
                i = 0
        return chunks

def get_chunker():
    return BasicChunker()
