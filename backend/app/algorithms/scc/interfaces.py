from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel

class Cluster(BaseModel):
    lead_memory: Dict[str, Any]
    supporting_memories: List[Dict[str, Any]]

class ExtractedFact(BaseModel):
    source_id: str
    fact_text: str

class CompressedContextResult(BaseModel):
    compressed_context: str
    compression_ratio: float
    original_memory_count: int
    compressed_memory_count: int

class ClusteringStrategy(ABC):
    @abstractmethod
    def cluster(self, ranked_memories: List[Dict[str, Any]]) -> List[Cluster]:
        pass

class DeduplicationStrategy(ABC):
    @abstractmethod
    def deduplicate(self, cluster: Cluster) -> Cluster:
        pass

class FactExtractionStrategy(ABC):
    @abstractmethod
    def extract_facts(self, cluster: Cluster) -> List[ExtractedFact]:
        pass

class SummarizationStrategy(ABC):
    @abstractmethod
    def summarize(self, facts: List[ExtractedFact]) -> str:
        pass
