from dataclasses import dataclass
from typing import List, Dict
import statistics
import json
import csv

@dataclass
class BenchmarkResult:
    pipeline: str
    conversation_size: int
    iteration: int
    original_tokens: int
    final_prompt_tokens: int
    token_reduction: int
    token_reduction_percentage: float
    retrieval_count: int
    selected_memory_count: int
    compression_ratio: float
    retrieval_latency: float
    cam_latency: float
    scc_latency: float
    apc_latency: float
    total_pipeline_latency: float
    relevant_facts_originally_present: int
    relevant_facts_retained: int
    relevant_fact_retention_percentage: float
    irrelevant_information_removed_percentage: float

def calculate_stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {}
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stddev": statistics.stdev(values) if len(values) > 1 else 0.0
    }

def save_results(results: List[BenchmarkResult], json_path: str = "benchmark_results.json", csv_path: str = "benchmark_results.csv"):
    res_dicts = [r.__dict__ for r in results]
    
    with open(json_path, 'w') as f:
        json.dump(res_dicts, f, indent=4)
        
    if res_dicts:
        keys = res_dicts[0].keys()
        with open(csv_path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(res_dicts)
