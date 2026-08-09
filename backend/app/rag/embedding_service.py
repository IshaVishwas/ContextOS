from typing import List
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Load the sentence transformer model
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.
        """
        embedding = self.model.encode(text)
        return embedding.tolist()

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of text strings.
        """
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

# Singleton instance
embedding_service = EmbeddingService()
