from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        # Load a pre-trained sentence-transformer model
        # all-MiniLM-L6-v2 provides a good balance of performance and size
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def embed_text(self, text: str) -> list[float]:
        # Generate embedding for a given text
        embedding = self.model.encode(text, convert_to_numpy=False, convert_to_tensor=False) # Return as list of floats
        return embedding.tolist()

embedding_service = EmbeddingService()
