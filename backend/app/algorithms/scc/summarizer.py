from typing import List
from .interfaces import FactExtractionStrategy, SummarizationStrategy, Cluster, ExtractedFact
import re

class PlaceholderFactExtractor(FactExtractionStrategy):
    def extract_facts(self, cluster: Cluster) -> List[ExtractedFact]:
        facts = []
        # Extract from lead
        lead_doc = cluster.lead_memory.get("document", "")
        lead_id = cluster.lead_memory.get("id", "unknown")
        
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?]) +', lead_doc)
        for s in sentences:
            if s.strip():
                facts.append(ExtractedFact(source_id=lead_id, fact_text=s.strip()))

        # Extract from supporters
        for support in cluster.supporting_memories:
            doc = support.get("document", "")
            s_id = support.get("id", "unknown")
            sentences = re.split(r'(?<=[.!?]) +', doc)
            # Take only the first sentence as a summary for supporters to reduce size
            if sentences and sentences[0].strip():
                facts.append(ExtractedFact(source_id=s_id, fact_text=sentences[0].strip()))

        return facts

class PlaceholderSummarizer(SummarizationStrategy):
    def summarize(self, facts: List[ExtractedFact]) -> str:
        # Concatenate facts
        summary_lines = []
        for fact in facts:
            summary_lines.append(f"- {fact.fact_text}")
        
        return "\n".join(summary_lines)
