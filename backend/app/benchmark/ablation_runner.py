import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.benchmark.dataset import get_benchmark_datasets
from app.benchmark.ablation import run_ablation
from app.benchmark.metrics import save_results
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
    
    # Check vector count before and after
    from app.rag.vector_store import vector_store
    try:
        col = vector_store.client.get_collection("memories")
        print(f"      [Clear DB] Vectors before: {col.count()}")
        vector_store.client.delete_collection("memories")
        print(f"      [Clear DB] Vectors after: 0 (collection deleted)")
    except Exception:
        pass

def main():
    print("==================================================")
    print("Starting Final Research Benchmark & Ablation Study")
    print("==================================================")
    
    datasets = get_benchmark_datasets()
    ITERATIONS = 5
    
    pipelines = [
        "baseline",
        "retriever",
        "retriever_cam",
        "retriever_cam_scc",
        "full_contextos",
        "scc_query_distance",
        "fixed_top_k"
    ]
    
    results = []
    
    for data in datasets:
        size = data["size"]
        print(f"\nProcessing size: {size} messages")
        
        for pipe in pipelines:
            # We don't need to run scc_query_distance and fixed_top_k for all sizes, but doing it is fine
            print(f"  Pipeline: {pipe}")
            for i in range(ITERATIONS):
                print(f"    Iteration {i+1}/{ITERATIONS}")
                clear_db()
                res = run_ablation(iteration=i, data=data, pipeline_type=pipe)
                results.append(res)
                save_results(results)

    print("\nBenchmark Complete.")
    
    # Generate report
    import app.benchmark.report as report_gen
    report_gen.generate_ablation_report(results)

if __name__ == "__main__":
    main()
