import pytest
from app.algorithms.cam.cam_engine import CAMEngine
from app.algorithms.cam.config import CAMConfig

def test_cam_engine_scoring_and_sorting():
    # Setup
    engine = CAMEngine()
    
    # Override config for predictable testing
    engine.ranker.weights = {
        "semantic_similarity": 0.5,
        "importance": 0.5,
        "recency": 0.0,
        "frequency": 0.0,
        "conversation_dependency": 0.0
    }

    # Mock raw memories
    raw_memories = [
        {
            "id": "1",
            "document": "Doc A",
            "distance": 0.0, # similarity score = 1 / (1+0) = 1.0 * 0.5 = 0.5
            "metadata": {"importance_score": 0.2} # 0.2 * 0.5 = 0.1, Total = 0.6
        },
        {
            "id": "2",
            "document": "Doc B",
            "distance": 1.0, # similarity score = 1 / (1+1) = 0.5 * 0.5 = 0.25
            "metadata": {"importance_score": 0.8} # 0.8 * 0.5 = 0.4, Total = 0.65
        },
        {
            "id": "3",
            "document": "Doc C",
            "distance": 0.0, # similarity = 1.0 * 0.5 = 0.5
            "metadata": {"importance_score": 1.0} # 1.0 * 0.5 = 0.5, Total = 1.0
        }
    ]

    # Execute
    ranked = engine.rank(raw_memories)

    # Assertions
    assert len(ranked) == 3
    # Should be sorted descending by cam_score: 3 (1.0), 2 (0.65), 1 (0.6)
    assert ranked[0]["id"] == "3"
    assert ranked[0]["cam_score"] == 1.0
    
    assert ranked[1]["id"] == "2"
    assert ranked[1]["cam_score"] == 0.65
    
    assert ranked[2]["id"] == "1"
    assert ranked[2]["cam_score"] == 0.6

    # Verify breakdown exists
    assert "semantic_similarity" in ranked[0]["breakdown"]
    assert "importance" in ranked[0]["breakdown"]

def test_conversation_dependency():
    engine = CAMEngine()
    engine.ranker.weights = {
        "semantic_similarity": 0.0,
        "importance": 0.0,
        "recency": 0.0,
        "frequency": 0.0,
        "conversation_dependency": 1.0
    }

    raw_memories = [
        {
            "id": "1",
            "metadata": {"conversation_id": 10},
            "distance": 0.0
        },
        {
            "id": "2",
            "metadata": {"conversation_id": 99},
            "distance": 0.0
        }
    ]

    ranked = engine.rank(raw_memories, query_context={"conversation_id": 99})

    assert ranked[0]["id"] == "2"
    assert ranked[0]["cam_score"] == 1.0
    assert ranked[1]["id"] == "1"
    assert ranked[1]["cam_score"] == 0.0
