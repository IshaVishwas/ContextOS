import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.algorithms.scc.compressor import scc_engine
from app.algorithms.scc.config import SCCConfig

def run_experiment():
    print("=== SCC Failure Mode Experiment ===")
    
    # We create two completely distinct memories that happen to have similar
    # vector distance to the query.
    # Query was "What is my configuration?"
    
    memories = [
        {
            "id": "mem_1",
            "document": "My preferred language is Python.",
            "distance": 0.40  # Distance to query
        },
        {
            "id": "mem_2",
            "document": "My production database is PostgreSQL.",
            "distance": 0.41  # Very similar distance to query!
        },
        {
            "id": "mem_3",
            "document": "My deployment region is Mumbai.",
            "distance": 0.42  # Very similar distance to query!
        }
    ]
    
    print(f"SCCConfig.CLUSTERING_SIMILARITY_THRESHOLD: {SCCConfig.CLUSTERING_SIMILARITY_THRESHOLD}")
    print(f"SCCConfig.DEDUPLICATION_SIMILARITY_THRESHOLD: {SCCConfig.DEDUPLICATION_SIMILARITY_THRESHOLD}")
    
    result = scc_engine.compress(memories)
    
    print("\nMemories Input:")
    for m in memories:
        print(f"- {m['document']} (dist: {m['distance']})")
        
    print(f"\nOriginal Memory Count: {result.original_memory_count}")
    print(f"Compressed Memory Count: {result.compressed_memory_count}")
    print("\nCompressed Context Output:")
    print(result.compressed_context)

if __name__ == "__main__":
    run_experiment()
