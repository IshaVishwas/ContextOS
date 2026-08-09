import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict, Any, Optional

class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

    def insert_vector(self, collection_name: str, id: str, vector: List[float], metadata: Dict[str, Any], document: str = ""):
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            embeddings=[vector],
            metadatas=[metadata],
            ids=[id],
            documents=[document]
        )

    def update_vector(self, collection_name: str, id: str, vector: List[float], metadata: Dict[str, Any], document: str = ""):
        collection = self.get_or_create_collection(collection_name)
        collection.update(
            embeddings=[vector],
            metadatas=[metadata],
            ids=[id],
            documents=[document]
        )

    def delete_vector(self, collection_name: str, id: str):
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=[id])

    def similarity_search(
        self, 
        collection_name: str, 
        query_vector: List[float], 
        top_k: int = 5, 
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        collection = self.get_or_create_collection(collection_name)
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=metadata_filter,
            include=["embeddings", "documents", "metadatas", "distances"]
        )
        return results

    def get_vector(self, collection_name: str, id: str) -> Dict[str, Any]:
        collection = self.get_or_create_collection(collection_name)
        return collection.get(ids=[id], include=["embeddings", "metadatas", "documents"])

vector_store = VectorStore()
