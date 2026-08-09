from typing import Dict, Any, List
from .interfaces import RankedMemory
from .config import CAMConfig
from .scoring import (
    SemanticScorer,
    RecencyScorer,
    ImportanceScorer,
    FrequencyScorer,
    ConversationDependencyScorer
)

class MemoryRanker:
    def __init__(self):
        self.scorers = {
            "semantic_similarity": SemanticScorer(),
            "recency": RecencyScorer(),
            "importance": ImportanceScorer(),
            "frequency": FrequencyScorer(),
            "conversation_dependency": ConversationDependencyScorer()
        }
        self.weights = CAMConfig.WEIGHTS

    def rank_memories(self, raw_memories: List[Dict[str, Any]], query_context: Dict[str, Any] = None) -> List[RankedMemory]:
        ranked = []
        for memory in raw_memories:
            total_score = 0.0
            breakdown = {}
            for key, scorer in self.scorers.items():
                score = scorer.score(memory, query_context)
                weight = self.weights.get(key, 0.0)
                weighted_score = score * weight
                breakdown[key] = weighted_score
                total_score += weighted_score

            ranked.append(RankedMemory(
                id=memory.get("id", ""),
                document=memory.get("document", ""),
                metadata=memory.get("metadata", {}),
                distance=memory.get("distance", 0.0),
                cam_score=total_score,
                breakdown=breakdown
            ))

        # Sort by cam_score descending
        ranked.sort(key=lambda x: x.cam_score, reverse=True)
        return ranked
