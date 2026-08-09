import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.rag.embedding_service import embedding_service
import numpy as np

def get_cosine_similarity(v1, v2):
    arr1 = np.array(v1)
    arr2 = np.array(v2)
    return np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2))

def main():
    s1 = "Important note: The user's primary programming language is Python. Please remember this."
    s2 = "Important note: The database uses PostgreSQL version 15. Please remember this."
    s3 = "Important note: The critical threshold for scaling is 95%. Please remember this."
    
    e1, e2, e3 = embedding_service.generate_batch_embeddings([s1, s2, s3])
    
    print(f"Similarity s1 vs s2: {get_cosine_similarity(e1, e2)}")
    print(f"Similarity s1 vs s3: {get_cosine_similarity(e1, e3)}")
    print(f"Similarity s2 vs s3: {get_cosine_similarity(e2, e3)}")

if __name__ == "__main__":
    main()
