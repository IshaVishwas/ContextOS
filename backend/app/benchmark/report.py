import json
from collections import defaultdict
from app.benchmark.metrics import calculate_stats

def generate_report(json_path: str = "benchmark_results.json"):
    with open(json_path, 'r') as f:
        results = json.load(f)
        
    # Group by size and pipeline
    # grouped[size][pipeline][metric] = list of values
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for r in results:
        size = r['conversation_size']
        pipe = r['pipeline']
        
        grouped[size][pipe]['original_tokens'].append(r['original_tokens'])
        grouped[size][pipe]['final_prompt_tokens'].append(r['final_prompt_tokens'])
        grouped[size][pipe]['token_reduction_percentage'].append(r['token_reduction_percentage'])
        grouped[size][pipe]['compression_ratio'].append(r['compression_ratio'])
        grouped[size][pipe]['relevant_fact_retention_percentage'].append(r['relevant_fact_retention_percentage'])
        grouped[size][pipe]['irrelevant_information_removed_percentage'].append(r['irrelevant_information_removed_percentage'])
        grouped[size][pipe]['total_pipeline_latency'].append(r['total_pipeline_latency'])
        grouped[size][pipe]['selected_memory_count'].append(r['selected_memory_count'])
        
    print("=" * 80)
    print("CONTEXTOS RESEARCH BENCHMARK REPORT")
    print("=" * 80)
    
    for size in sorted(grouped.keys()):
        print(f"\nConversation Size: {size} messages")
        print("-" * 80)
        
        baseline = grouped[size].get('baseline', {})
        contextos = grouped[size].get('contextos', {})
        
        metrics_to_print = [
            ("Prompt Tokens", "final_prompt_tokens", False),
            ("Token Reduction %", "token_reduction_percentage", True),
            ("Compression Ratio", "compression_ratio", False),
            ("Fact Retention %", "relevant_fact_retention_percentage", True),
            ("Irrelevant Info Removed %", "irrelevant_information_removed_percentage", True),
            ("Total Latency (s)", "total_pipeline_latency", False),
            ("Memory Count", "selected_memory_count", False),
        ]
        
        print(f"{'Metric':<30} | {'Baseline (Mean)':<20} | {'ContextOS (Mean)':<20}")
        print("-" * 80)
        
        for name, key, is_percent in metrics_to_print:
            b_vals = baseline.get(key, [0])
            c_vals = contextos.get(key, [0])
            
            b_stats = calculate_stats(b_vals)
            c_stats = calculate_stats(c_vals)
            
            b_mean = b_stats.get('mean', 0)
            c_mean = c_stats.get('mean', 0)
            
            fmt = "{:.2f}%" if is_percent else "{:.4f}"
            b_str = fmt.format(b_mean)
            c_str = fmt.format(c_mean)
            
            print(f"{name:<30} | {b_str:<20} | {c_str:<20}")
            
        print("\nStatistical Breakdown (ContextOS):")
        # Print detailed stats for ContextOS tokens and retention
        for key in ['final_prompt_tokens', 'relevant_fact_retention_percentage', 'total_pipeline_latency']:
            stats = calculate_stats(contextos.get(key, [0]))
            print(f"  {key}:")
            for sk, sv in stats.items():
                print(f"    {sk}: {sv:.4f}")

def generate_ablation_report(results, json_path: str = "benchmark_results.json"):
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for r in results:
        # Use object dict if it's an object, otherwise assume dict (when loading from JSON)
        r_dict = r.__dict__ if hasattr(r, '__dict__') else r
        size = r_dict['conversation_size']
        pipe = r_dict['pipeline']
        
        grouped[size][pipe]['original_tokens'].append(r_dict['original_tokens'])
        grouped[size][pipe]['final_prompt_tokens'].append(r_dict['final_prompt_tokens'])
        grouped[size][pipe]['token_reduction_percentage'].append(r_dict['token_reduction_percentage'])
        grouped[size][pipe]['compression_ratio'].append(r_dict['compression_ratio'])
        grouped[size][pipe]['relevant_fact_retention_percentage'].append(r_dict['relevant_fact_retention_percentage'])
        grouped[size][pipe]['irrelevant_information_removed_percentage'].append(r_dict['irrelevant_information_removed_percentage'])
        grouped[size][pipe]['retrieval_latency'].append(r_dict['retrieval_latency'])
        grouped[size][pipe]['cam_latency'].append(r_dict['cam_latency'])
        grouped[size][pipe]['scc_latency'].append(r_dict['scc_latency'])
        grouped[size][pipe]['apc_latency'].append(r_dict['apc_latency'])
        grouped[size][pipe]['total_pipeline_latency'].append(r_dict['total_pipeline_latency'])
        grouped[size][pipe]['selected_memory_count'].append(r_dict['selected_memory_count'])
        grouped[size][pipe]['retrieval_count'].append(r_dict['retrieval_count'])

    pipelines = [
        "baseline",
        "retriever",
        "retriever_cam",
        "retriever_cam_scc",
        "full_contextos",
        "scc_query_distance",
        "fixed_top_k"
    ]
    
    report_lines = []
    report_lines.append("# Final Research Benchmark & Ablation Study Report\n")
    
    for size in sorted(grouped.keys()):
        report_lines.append(f"## Conversation Size: {size} messages\n")
        
        # 1. Main Ablation Table
        report_lines.append("### Component Ablation\n")
        report_lines.append("| Pipeline | Prompt Tokens | Token Reduction % | Fact Retention % | Total Latency (s) |")
        report_lines.append("|---|---|---|---|---|")
        
        for p in ["baseline", "retriever", "retriever_cam", "retriever_cam_scc", "full_contextos"]:
            if p not in grouped[size]: continue
            p_data = grouped[size][p]
            tokens = calculate_stats(p_data['final_prompt_tokens']).get('mean', 0)
            red = calculate_stats(p_data['token_reduction_percentage']).get('mean', 0)
            ret = calculate_stats(p_data['relevant_fact_retention_percentage']).get('mean', 0)
            lat = calculate_stats(p_data['total_pipeline_latency']).get('mean', 0)
            report_lines.append(f"| {p} | {tokens:.1f} | {red:.2f}% | {ret:.2f}% | {lat:.4f} |")
        
        # 2. Latency Breakdown
        report_lines.append("\n### Latency Breakdown\n")
        report_lines.append("| Pipeline | Retriever (s) | CAM (s) | SCC (s) | APC (s) | Total (s) |")
        report_lines.append("|---|---|---|---|---|---|")
        for p in ["baseline", "retriever", "retriever_cam", "retriever_cam_scc", "full_contextos"]:
            if p not in grouped[size]: continue
            p_data = grouped[size][p]
            rl = calculate_stats(p_data['retrieval_latency']).get('mean', 0)
            cl = calculate_stats(p_data['cam_latency']).get('mean', 0)
            sl = calculate_stats(p_data['scc_latency']).get('mean', 0)
            al = calculate_stats(p_data['apc_latency']).get('mean', 0)
            tl = calculate_stats(p_data['total_pipeline_latency']).get('mean', 0)
            report_lines.append(f"| {p} | {rl:.4f} | {cl:.4f} | {sl:.4f} | {al:.4f} | {tl:.4f} |")
            
        # 3. Targeted Ablations (if 250 messages)
        if size == 250:
            report_lines.append("\n### SCC Ablation (250 messages)\n")
            report_lines.append("| SCC Logic | Fact Retention % | Token Reduction % | Total Latency (s) | Selected Candidates |")
            report_lines.append("|---|---|---|---|---|")
            for p, label in [("scc_query_distance", "Sprint 16 (Query Distance)"), ("retriever_cam_scc", "Sprint 17 (Cosine Similarity)")]:
                if p not in grouped[size]: continue
                p_data = grouped[size][p]
                ret = calculate_stats(p_data['relevant_fact_retention_percentage']).get('mean', 0)
                red = calculate_stats(p_data['token_reduction_percentage']).get('mean', 0)
                lat = calculate_stats(p_data['total_pipeline_latency']).get('mean', 0)
                cand = calculate_stats(p_data['selected_memory_count']).get('mean', 0)
                report_lines.append(f"| {label} | {ret:.2f}% | {red:.2f}% | {lat:.4f} | {cand:.1f} |")
                
            report_lines.append("\n### Adaptive Retrieval Ablation (250 messages)\n")
            report_lines.append("| Retrieval Logic | Fact Retention % | Token Reduction % | Total Latency (s) | Retrieved Candidates |")
            report_lines.append("|---|---|---|---|---|")
            for p, label in [("fixed_top_k", "Fixed top_k=5"), ("retriever_cam_scc", "Adaptive Retrieval")]:
                if p not in grouped[size]: continue
                p_data = grouped[size][p]
                ret = calculate_stats(p_data['relevant_fact_retention_percentage']).get('mean', 0)
                red = calculate_stats(p_data['token_reduction_percentage']).get('mean', 0)
                lat = calculate_stats(p_data['total_pipeline_latency']).get('mean', 0)
                cand = calculate_stats(p_data['retrieval_count']).get('mean', 0)
                report_lines.append(f"| {label} | {ret:.2f}% | {red:.2f}% | {lat:.4f} | {cand:.1f} |")
                
        report_lines.append("\n---\n")

    report_content = "\n".join(report_lines)
    with open("final_benchmark_report.md", "w") as f:
        f.write(report_content)
    
    print("Generated final_benchmark_report.md")

