from typing import Dict, Any, List
from .memory_ranker import MemoryRanker

class CAMEngine:
    def __init__(self):
        self.ranker = MemoryRanker()

    def rank(self, raw_memories: List[Dict[str, Any]], query_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        ranked_objects = self.ranker.rank_memories(raw_memories, query_context)
        # Convert back to dict to maintain API compatibility
        return [obj.model_dump() for obj in ranked_objects]

cam_engine = CAMEngine()
