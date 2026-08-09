from typing import List, Dict, Any
from .interfaces import CompressedContextResult
from .clusterer import SemanticClusterer, RedundancyFilter
from .summarizer import PlaceholderFactExtractor, PlaceholderSummarizer

class SCCEngine:
    def __init__(self):
        self.clusterer = SemanticClusterer()
        self.deduplicator = RedundancyFilter()
        self.extractor = PlaceholderFactExtractor()
        self.summarizer = PlaceholderSummarizer()

    def compress(self, ranked_memories: List[Dict[str, Any]]) -> CompressedContextResult:
        if not ranked_memories:
            return CompressedContextResult(
                compressed_context="",
                compression_ratio=0.0,
                original_memory_count=0,
                compressed_memory_count=0
            )

        original_count = len(ranked_memories)

        # 1. Semantic Clustering
        clusters = self.clusterer.cluster(ranked_memories)

        # 2. Duplicate Removal
        deduplicated_clusters = [self.deduplicator.deduplicate(c) for c in clusters]

        # 3. Fact Extraction
        all_facts = []
        for c in deduplicated_clusters:
            all_facts.extend(self.extractor.extract_facts(c))

        # 4. Summarization (Compressed Context)
        compressed_context = self.summarizer.summarize(all_facts)

        # Calculate metrics
        # The number of compressed memories is roughly the number of clusters (lead memories) + unique supporters
        compressed_count = sum(1 + len(c.supporting_memories) for c in deduplicated_clusters)
        
        # Original char count vs Compressed char count for ratio
        original_char_count = sum(len(m.get("document", "")) for m in ranked_memories)
        compressed_char_count = len(compressed_context)
        
        ratio = 0.0
        if original_char_count > 0:
            ratio = (original_char_count - compressed_char_count) / original_char_count
            # Ensure ratio isn't negative if the placeholder added markdown bullets that made it longer
            ratio = max(0.0, ratio)

        return CompressedContextResult(
            compressed_context=compressed_context,
            compression_ratio=ratio,
            original_memory_count=original_count,
            compressed_memory_count=compressed_count
        )

scc_engine = SCCEngine()
