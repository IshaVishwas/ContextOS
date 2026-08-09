import os
import sys

# Add backend to path if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.benchmark.dataset import get_benchmark_datasets
from app.benchmark.baseline import run_baseline
from app.benchmark.contextos import run_contextos
from app.benchmark.metrics import save_results
from app.benchmark.report import generate_report
from app.db.session import SessionLocal
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.memory import Memory

def clear_db():
    db = SessionLocal()
    try:
        db.query(Memory).delete()
        db.query(Message).delete()
        db.query(Conversation).delete()
        db.commit()
    finally:
        db.close()
    
    # Also clear ChromaDB to prevent cross-contamination between runs
    from app.rag.vector_store import vector_store
    try:
        vector_store.client.delete_collection("memories")
    except Exception:
        pass

def main():
    print("Starting Benchmark...")
    datasets = get_benchmark_datasets()
    
    ITERATIONS = 3 # Number of times to run each size to get mean/stddev
    
    results = []
    
    for data in datasets:
        size = data["size"]
        print(f"\nProcessing size: {size} messages")
        
        for i in range(ITERATIONS):
            print(f"  Iteration {i+1}/{ITERATIONS}")
            
            # Run Baseline
            res_base = run_baseline(iteration=i, data=data)
            results.append(res_base)
            
            # Clear DB before ContextOS run to avoid cross-contamination
            clear_db()
            
            # Run ContextOS
            res_ctx = run_contextos(iteration=i, data=data)
            results.append(res_ctx)
            
            # Save intermediate
            save_results(results)

    print("\nBenchmark Complete.")
    generate_report()

if __name__ == "__main__":
    main()
