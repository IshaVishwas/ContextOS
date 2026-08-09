from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel

class RankedMemory(BaseModel):
    id: str
    document: str
    metadata: Dict[str, Any]
    distance: float
    cam_score: float = 0.0
    breakdown: Dict[str, float] = {}

class ScoringStrategy(ABC):
    @abstractmethod
    def score(self, memory: Dict[str, Any], query_context: Dict[str, Any] = None) -> float:
        """
        Calculates a score between 0.0 and 1.0 for a given memory.
        """
        pass
