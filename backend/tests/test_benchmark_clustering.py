import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.benchmark.dataset import generate_conversation
from app.algorithms.scc.compressor import scc_engine
from app.rag.embedding_service import embedding_service

def main():
    data = generate_conversation(50)
    messages = data["messages"]
    
    # Create fake memories from messages
    memories = []
    for i, msg in enumerate(messages):
        memories.append({
            "id": f"m{i}",
            "document": msg["content"],
            "distance": 0.5 # arbitrary
        })
        
    result = scc_engine.compress(memories)
    
    print(f"Original Count: {result.original_memory_count}")
    print(f"Compressed Count: {result.compressed_memory_count}")
    print("Compressed Context:")
    print(result.compressed_context)

if __name__ == "__main__":
    main()
