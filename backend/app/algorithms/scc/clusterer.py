import numpy as np
from typing import List, Dict, Any
from .interfaces import ClusteringStrategy, DeduplicationStrategy, Cluster
from .config import SCCConfig
from app.rag.embedding_service import embedding_service

def get_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2:
        return 0.0
    arr1 = np.array(v1)
    arr2 = np.array(v2)
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return np.dot(arr1, arr2) / (norm1 * norm2)

def _ensure_embeddings(memories: List[Dict[str, Any]]) -> None:
    # Check if any memory is missing embeddings
    missing_indices = []
    texts_to_embed = []
    
    for i, memory in enumerate(memories):
        if not memory.get("embedding"):
            missing_indices.append(i)
            texts_to_embed.append(memory.get("document", ""))
            
    if missing_indices:
        # Batch generate missing embeddings
        new_embeddings = embedding_service.generate_batch_embeddings(texts_to_embed)
        for idx, emb in zip(missing_indices, new_embeddings):
            memories[idx]["embedding"] = emb

class SemanticClusterer(ClusteringStrategy):
    def cluster(self, ranked_memories: List[Dict[str, Any]]) -> List[Cluster]:
        clusters = []
        used_ids = set()

        _ensure_embeddings(ranked_memories)

        for memory in ranked_memories:
            mem_id = memory.get("id")
            if mem_id in used_ids:
                continue
            
            # Form a new cluster
            cluster = Cluster(lead_memory=memory, supporting_memories=[])
            used_ids.add(mem_id)

            lead_embedding = memory.get("embedding", [])
            
            for other in ranked_memories:
                other_id = other.get("id")
                if other_id not in used_ids:
                    other_embedding = other.get("embedding", [])
                    similarity = get_cosine_similarity(lead_embedding, other_embedding)
                    
                    if similarity >= SCCConfig.CLUSTERING_SIMILARITY_THRESHOLD:
                        cluster.supporting_memories.append(other)
                        used_ids.add(other_id)

            clusters.append(cluster)

        return clusters

class RedundancyFilter(DeduplicationStrategy):
    def deduplicate(self, cluster: Cluster) -> Cluster:
        # Keep lead memory, remove supporting memories that are too similar (redundant)
        lead_embedding = cluster.lead_memory.get("embedding", [])
        filtered_supporters = []
        
        for support in cluster.supporting_memories:
            support_embedding = support.get("embedding", [])
            similarity = get_cosine_similarity(lead_embedding, support_embedding)
            
            # If similarity is LESS than threshold, it's NOT an exact duplicate
            # meaning it holds some unique context despite being in the same cluster.
            if similarity < SCCConfig.DEDUPLICATION_SIMILARITY_THRESHOLD:
                filtered_supporters.append(support)
        
        cluster.supporting_memories = filtered_supporters
        return cluster
