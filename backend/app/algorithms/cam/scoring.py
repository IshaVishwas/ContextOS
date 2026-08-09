from typing import Dict, Any
from .interfaces import ScoringStrategy

class SemanticScorer(ScoringStrategy):
    def score(self, memory: Dict[str, Any], query_context: Dict[str, Any] = None) -> float:
        # Distance from ChromaDB (L2). Lower is better.
        # We invert it so higher score is better.
        distance = memory.get("distance", 1.0)
        return 1.0 / (1.0 + distance)

class RecencyScorer(ScoringStrategy):
    def score(self, memory: Dict[str, Any], query_context: Dict[str, Any] = None) -> float:
        # Placeholder for actual recency scoring logic using metadata timestamps
        return 0.5 

class ImportanceScorer(ScoringStrategy):
    def score(self, memory: Dict[str, Any], query_context: Dict[str, Any] = None) -> float:
        metadata = memory.get("metadata", {})
        return float(metadata.get("importance_score", 0.5))

class FrequencyScorer(ScoringStrategy):
    def score(self, memory: Dict[str, Any], query_context: Dict[str, Any] = None) -> float:
        metadata = memory.get("metadata", {})
        access_count = metadata.get("access_count", 1)
        # Simple log-like scale
        return min(1.0, access_count / 10.0)

class ConversationDependencyScorer(ScoringStrategy):
    def score(self, memory: Dict[str, Any], query_context: Dict[str, Any] = None) -> float:
        metadata = memory.get("metadata", {})
        if query_context and "conversation_id" in query_context:
            if metadata.get("conversation_id") == query_context["conversation_id"]:
                return 1.0
        return 0.0
