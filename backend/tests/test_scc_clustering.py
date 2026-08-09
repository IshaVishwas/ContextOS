import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.algorithms.scc.clusterer import SemanticClusterer, RedundancyFilter, get_cosine_similarity
from app.algorithms.scc.config import SCCConfig
from app.algorithms.scc.interfaces import Cluster

@pytest.fixture
def mock_embedding_service():
    with patch("app.algorithms.scc.clusterer.embedding_service") as mock_svc:
        yield mock_svc

def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    
    assert get_cosine_similarity(v1, v2) == 1.0
    assert get_cosine_similarity(v1, v3) == 0.0
    assert get_cosine_similarity([], v1) == 0.0

def test_empty_input():
    clusterer = SemanticClusterer()
    clusters = clusterer.cluster([])
    assert len(clusters) == 0

def test_single_memory():
    clusterer = SemanticClusterer()
    memories = [
        {"id": "m1", "document": "Hello", "embedding": [1.0, 0.0]}
    ]
    clusters = clusterer.cluster(memories)
    assert len(clusters) == 1
    assert clusters[0].lead_memory["id"] == "m1"
    assert len(clusters[0].supporting_memories) == 0

def test_identical_memories_deduplicate():
    clusterer = SemanticClusterer()
    memories = [
        {"id": "m1", "document": "Python is great", "embedding": [1.0, 0.0, 0.0]},
        {"id": "m2", "document": "Python is great", "embedding": [1.0, 0.0, 0.0]}
    ]
    
    clusters = clusterer.cluster(memories)
    # Should form 1 cluster because similarity is 1.0 >= 0.70
    assert len(clusters) == 1
    assert len(clusters[0].supporting_memories) == 1
    
    filter = RedundancyFilter()
    deduped = filter.deduplicate(clusters[0])
    
    # The supporter should be dropped because similarity 1.0 >= 0.95
    assert len(deduped.supporting_memories) == 0

def test_near_duplicate_memories_deduplicate():
    clusterer = SemanticClusterer()
    memories = [
        {"id": "m1", "document": "I love Python.", "embedding": [0.99, 0.1, 0.0]},
        {"id": "m2", "document": "Python is my favorite.", "embedding": [0.98, 0.12, 0.0]} # Cosine sim ~0.999
    ]
    
    clusters = clusterer.cluster(memories)
    assert len(clusters) == 1
    
    filter = RedundancyFilter()
    deduped = filter.deduplicate(clusters[0])
    
    # Should be dropped because it's a near duplicate (sim > 0.95)
    assert len(deduped.supporting_memories) == 0

def test_distinct_facts_preserve():
    clusterer = SemanticClusterer()
    memories = [
        {"id": "m1", "document": "My DB is PostgreSQL.", "embedding": [1.0, 0.0, 0.0]},
        {"id": "m2", "document": "My language is Python.", "embedding": [0.0, 1.0, 0.0]}
    ]
    
    clusters = clusterer.cluster(memories)
    
    # Similarity is 0.0 < 0.70, so they form distinct clusters
    assert len(clusters) == 2

def test_distinct_facts_same_query_relevance():
    # To simulate the exact failure mode:
    # They form distinct clusters because their content embeddings are orthogonal,
    # even though their distance from the query (not used here) might have been similar.
    clusterer = SemanticClusterer()
    memories = [
        {"id": "m1", "document": "PostgreSQL", "embedding": [1.0, 0.0, 0.0], "distance": 0.4},
        {"id": "m2", "document": "Python", "embedding": [0.0, 1.0, 0.0], "distance": 0.41}
    ]
    
    clusters = clusterer.cluster(memories)
    
    # Similarity between m1 and m2 is 0.0. 
    # Under old logic, abs(0.4 - 0.41) = 0.01 < 0.2, so they would cluster.
    # Under new logic, they don't.
    assert len(clusters) == 2

def test_unrelated_memories():
    clusterer = SemanticClusterer()
    memories = [
        {"id": "m1", "document": "A", "embedding": [1.0, 0.0, 0.0]},
        {"id": "m2", "document": "B", "embedding": [0.0, 1.0, 0.0]},
        {"id": "m3", "document": "C", "embedding": [0.0, 0.0, 1.0]}
    ]
    
    clusters = clusterer.cluster(memories)
    assert len(clusters) == 3

def test_large_candidate_set(mock_embedding_service):
    # Ensure it works when embeddings need to be generated
    # mock_embedding_service.generate_batch_embeddings will return fake embeddings
    def fake_embed(texts):
        # Return a simple one-hot vector for each text
        res = []
        for i in range(len(texts)):
            vec = [0.0]*len(texts)
            vec[i] = 1.0
            res.append(vec)
        return res
        
    mock_embedding_service.generate_batch_embeddings.side_effect = fake_embed
    
    clusterer = SemanticClusterer()
    memories = [{"id": f"m{i}", "document": f"Fact {i}"} for i in range(50)]
    
    # Since all will have orthogonal embeddings, we should get 50 clusters
    clusters = clusterer.cluster(memories)
    
    assert len(clusters) == 50
    assert mock_embedding_service.generate_batch_embeddings.called

def test_adaptive_retrieval_output_format():
    # Simulates what comes out of Retriever when embeddings are already included
    clusterer = SemanticClusterer()
    memories = [
        {"id": "m1", "document": "PostgreSQL", "embedding": [1.0, 0.0, 0.0], "distance": 0.4},
        {"id": "m2", "document": "PostgreSQL 15", "embedding": [0.99, 0.1, 0.0], "distance": 0.41},
        {"id": "m3", "document": "Python", "embedding": [0.0, 1.0, 0.0], "distance": 0.42}
    ]
    
    clusters = clusterer.cluster(memories)
    
    # m1 and m2 should cluster (similarity ~0.99)
    # m3 should be separate
    assert len(clusters) == 2
    
    # Identify which cluster has m1/m2
    lead_m1_cluster = next(c for c in clusters if c.lead_memory["id"] == "m1")
    assert len(lead_m1_cluster.supporting_memories) == 1
    
    filter = RedundancyFilter()
    deduped = filter.deduplicate(lead_m1_cluster)
    
    # Support m2 should be dropped because sim > 0.95
    assert len(deduped.supporting_memories) == 0
