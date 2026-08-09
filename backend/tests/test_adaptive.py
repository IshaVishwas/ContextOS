import pytest
from app.rag.adaptive import AdaptiveRetrievalStrategy, AdaptiveConfig

def test_small_conversation_short_query():
    strategy = AdaptiveRetrievalStrategy()
    k = strategy.determine_k(conversation_size=10, query="Hello")
    assert k >= AdaptiveConfig.MIN_CANDIDATES
    assert k <= AdaptiveConfig.MIN_CANDIDATES + 2

def test_medium_conversation():
    strategy = AdaptiveRetrievalStrategy()
    k = strategy.determine_k(conversation_size=50, query="Hello")
    assert k > AdaptiveConfig.MIN_CANDIDATES

def test_large_conversation():
    strategy = AdaptiveRetrievalStrategy()
    k = strategy.determine_k(conversation_size=100, query="Hello")
    # Base = 50. Size_factor = 2. K = 5 * 3 = 15
    assert k >= 15

def test_very_large_conversation():
    strategy = AdaptiveRetrievalStrategy()
    k = strategy.determine_k(conversation_size=250, query="Hello")
    # Base = 50. Size_factor = 5. K = 5 * 6 = 30
    assert k >= 30

def test_long_query():
    strategy = AdaptiveRetrievalStrategy()
    query = "This is a very long query that has lots of words in it " * 10
    k = strategy.determine_k(conversation_size=10, query=query)
    # Query length 90 words * 0.1 = 9. Base K = 5. Total = ~14.
    assert k > AdaptiveConfig.MIN_CANDIDATES

def test_empty_results():
    strategy = AdaptiveRetrievalStrategy()
    filtered = strategy.filter_candidates([])
    assert filtered == []

def test_high_similarity_results():
    strategy = AdaptiveRetrievalStrategy()
    # High similarity means distances are very close and low
    results = [
        {"id": "1", "distance": 0.1},
        {"id": "2", "distance": 0.11},
        {"id": "3", "distance": 0.12},
        {"id": "4", "distance": 0.1},
        {"id": "5", "distance": 0.11},
        {"id": "6", "distance": 0.9} # outlier
    ]
    filtered = strategy.filter_candidates(results)
    assert len(filtered) == 5
    assert "6" not in [r["id"] for r in filtered]

def test_low_similarity_results():
    strategy = AdaptiveRetrievalStrategy()
    # All are somewhat bad, but clustered
    results = [
        {"id": "1", "distance": 0.8},
        {"id": "2", "distance": 0.85},
        {"id": "3", "distance": 0.9},
        {"id": "4", "distance": 0.88},
        {"id": "5", "distance": 0.82}
    ]
    filtered = strategy.filter_candidates(results)
    assert len(filtered) == 5

def test_existing_fixed_retrieval_compatibility():
    # Test that if we don't trigger adaptive, the strategy filter doesn't break
    strategy = AdaptiveRetrievalStrategy()
    results = [{"id": str(i), "distance": i * 0.1} for i in range(10)]
    # Normally retriever handles bypassing the filter if top_k is specified.
    # We just ensure filter_candidates doesn't throw errors on raw lists.
    filtered = strategy.filter_candidates(results)
    assert len(filtered) >= AdaptiveConfig.MIN_CANDIDATES
