import statistics
from typing import List, Dict, Any

class AdaptiveConfig:
    MIN_CANDIDATES = 5
    MAX_CANDIDATES = 50
    CONVERSATION_SIZE_BASE = 25 # Base normalization
    QUERY_LENGTH_FACTOR = 0.5   # Complexity multiplier

class AdaptiveRetrievalStrategy:
    def determine_k(self, conversation_size: int, query: str) -> int:
        """
        Dynamically calculate how many candidates to fetch from the DB.
        """
        # Base scaling factor depending on context size
        size_factor = conversation_size / AdaptiveConfig.CONVERSATION_SIZE_BASE
        
        # Word count complexity
        query_words = len(query.split())
        query_factor = query_words * AdaptiveConfig.QUERY_LENGTH_FACTOR
        
        # We start with minimum and scale up based on factors
        target_k = int(AdaptiveConfig.MIN_CANDIDATES * (1 + size_factor) + query_factor)
        
        # Cap between MIN and MAX
        return min(AdaptiveConfig.MAX_CANDIDATES, max(AdaptiveConfig.MIN_CANDIDATES, target_k))

    def filter_candidates(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Statistically prune candidates that are too far away from the relevant cluster.
        In ChromaDB (L2), lower distance = higher similarity.
        """
        if not results:
            return []
            
        distances = [r.get("distance", 0.0) for r in results if r.get("distance") is not None]
        if not distances:
            return results
            
        mean_dist = statistics.mean(distances)
        std_dist = statistics.stdev(distances) if len(distances) > 1 else 0.0
        
        # If std_dist is very small, they are all equally relevant/irrelevant
        # We drop candidates that are worse than (mean + stddev)
        threshold = mean_dist + std_dist
        
        filtered = [r for r in results if r.get("distance", 0.0) <= threshold]
        
        # Ensure we always return at least MIN_CANDIDATES if the original pool had them
        if len(filtered) < AdaptiveConfig.MIN_CANDIDATES and len(results) >= AdaptiveConfig.MIN_CANDIDATES:
            # Sort by distance (ascending) to guarantee we keep the best ones
            sorted_results = sorted(results, key=lambda x: x.get("distance", 0.0))
            filtered = sorted_results[:AdaptiveConfig.MIN_CANDIDATES]
            
        return filtered
