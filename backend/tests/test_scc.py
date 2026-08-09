import pytest
from app.algorithms.scc.compressor import SCCEngine
from app.algorithms.cam.interfaces import RankedMemory

def test_scc_clustering_and_deduplication():
    engine = SCCEngine()

    # Mock ranked memories directly as dicts (as returned by CAM engine)
    ranked_memories = [
        {
            "id": "1",
            "document": "The sky is blue today.",
            "distance": 0.1,
            "metadata": {}
        },
        {
            "id": "2",
            "document": "The sky is very blue today.",
            "distance": 0.11, # Will cluster with 1, distance diff is 0.01 < 0.2, and will be deduplicated because diff is < 0.05
            "metadata": {}
        },
        {
            "id": "3",
            "document": "I like apples.",
            "distance": 0.8, # Different cluster
            "metadata": {}
        },
        {
            "id": "4",
            "document": "Apples are great.",
            "distance": 0.9, # Will cluster with 3, distance diff is 0.1 < 0.2, but WON'T be deduplicated because diff > 0.05
            "metadata": {}
        }
    ]

    result = engine.compress(ranked_memories)

    assert result.original_memory_count == 4
    # Expected clusters:
    # Cluster 1: Lead (id=1, dist=0.1), Supporters: [id=2 (dist=0.11)]
    #   -> Deduplication: id=2 is removed because abs(0.1 - 0.11) = 0.01 < 0.05
    #   -> Remaining in Cluster 1: [id=1]
    #
    # Cluster 2: Lead (id=3, dist=0.8), Supporters: [id=4 (dist=0.9)]
    #   -> Deduplication: id=4 is KEPT because abs(0.8 - 0.9) = 0.1 > 0.05
    #   -> Remaining in Cluster 2: [id=3, id=4]
    # 
    # Total compressed memory count = 1 (from C1) + 2 (from C2) = 3
    assert result.compressed_memory_count == 3
    
    # Check that compressed_context contains the facts
    assert "The sky is blue today." in result.compressed_context
    assert "I like apples." in result.compressed_context
    assert "Apples are great." in result.compressed_context
    
    # "The sky is very blue today." should be stripped by deduplication
    assert "The sky is very blue today." not in result.compressed_context
    
    # Check compression ratio
    assert result.compression_ratio >= 0.0

def test_scc_empty_input():
    engine = SCCEngine()
    result = engine.compress([])
    
    assert result.original_memory_count == 0
    assert result.compressed_memory_count == 0
    assert result.compression_ratio == 0.0
    assert result.compressed_context == ""
