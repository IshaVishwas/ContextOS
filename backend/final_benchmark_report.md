# Final Research Benchmark & Ablation Study Report

## Conversation Size: 10 messages

### Component Ablation

| Pipeline | Prompt Tokens | Token Reduction % | Fact Retention % | Total Latency (s) |
|---|---|---|---|---|
| baseline | 249.0 | 0.00% | 100.00% | 0.0000 |
| retriever | 384.0 | 0.00% | 100.00% | 0.0186 |
| retriever_cam | 384.0 | 0.00% | 100.00% | 0.0182 |
| retriever_cam_scc | 375.0 | 0.00% | 100.00% | 0.0421 |
| full_contextos | 392.0 | 0.00% | 100.00% | 0.0419 |

### Latency Breakdown

| Pipeline | Retriever (s) | CAM (s) | SCC (s) | APC (s) | Total (s) |
|---|---|---|---|---|---|
| baseline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| retriever | 0.0186 | 0.0000 | 0.0000 | 0.0000 | 0.0186 |
| retriever_cam | 0.0180 | 0.0002 | 0.0000 | 0.0000 | 0.0182 |
| retriever_cam_scc | 0.0174 | 0.0002 | 0.0246 | 0.0000 | 0.0421 |
| full_contextos | 0.0173 | 0.0002 | 0.0243 | 0.0001 | 0.0419 |

---

## Conversation Size: 25 messages

### Component Ablation

| Pipeline | Prompt Tokens | Token Reduction % | Fact Retention % | Total Latency (s) |
|---|---|---|---|---|
| baseline | 501.0 | 0.00% | 100.00% | 0.0000 |
| retriever | 767.0 | 0.00% | 100.00% | 0.0206 |
| retriever_cam | 767.0 | 0.00% | 100.00% | 0.0197 |
| retriever_cam_scc | 674.0 | 0.00% | 100.00% | 0.0785 |
| full_contextos | 691.0 | 0.00% | 100.00% | 0.0725 |

### Latency Breakdown

| Pipeline | Retriever (s) | CAM (s) | SCC (s) | APC (s) | Total (s) |
|---|---|---|---|---|---|
| baseline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| retriever | 0.0205 | 0.0000 | 0.0000 | 0.0000 | 0.0206 |
| retriever_cam | 0.0194 | 0.0003 | 0.0000 | 0.0000 | 0.0197 |
| retriever_cam_scc | 0.0199 | 0.0003 | 0.0582 | 0.0000 | 0.0785 |
| full_contextos | 0.0215 | 0.0003 | 0.0506 | 0.0001 | 0.0725 |

---

## Conversation Size: 50 messages

### Component Ablation

| Pipeline | Prompt Tokens | Token Reduction % | Fact Retention % | Total Latency (s) |
|---|---|---|---|---|
| baseline | 936.0 | 0.00% | 100.00% | 0.0001 |
| retriever | 1311.0 | 0.00% | 100.00% | 0.0200 |
| retriever_cam | 1311.0 | 0.00% | 100.00% | 0.0198 |
| retriever_cam_scc | 1107.0 | 0.00% | 100.00% | 0.0793 |
| full_contextos | 1125.0 | 0.00% | 100.00% | 0.0805 |

### Latency Breakdown

| Pipeline | Retriever (s) | CAM (s) | SCC (s) | APC (s) | Total (s) |
|---|---|---|---|---|---|
| baseline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0001 |
| retriever | 0.0199 | 0.0000 | 0.0000 | 0.0000 | 0.0200 |
| retriever_cam | 0.0194 | 0.0003 | 0.0000 | 0.0000 | 0.0198 |
| retriever_cam_scc | 0.0199 | 0.0004 | 0.0590 | 0.0000 | 0.0793 |
| full_contextos | 0.0208 | 0.0004 | 0.0591 | 0.0002 | 0.0805 |

---

## Conversation Size: 100 messages

### Component Ablation

| Pipeline | Prompt Tokens | Token Reduction % | Fact Retention % | Total Latency (s) |
|---|---|---|---|---|
| baseline | 1773.0 | 0.00% | 100.00% | 0.0001 |
| retriever | 2291.0 | 0.00% | 100.00% | 0.0211 |
| retriever_cam | 2291.0 | 0.00% | 100.00% | 0.0223 |
| retriever_cam_scc | 1945.0 | 0.00% | 100.00% | 0.1066 |
| full_contextos | 1727.0 | 2.59% | 100.00% | 0.1075 |

### Latency Breakdown

| Pipeline | Retriever (s) | CAM (s) | SCC (s) | APC (s) | Total (s) |
|---|---|---|---|---|---|
| baseline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0001 |
| retriever | 0.0209 | 0.0000 | 0.0000 | 0.0000 | 0.0211 |
| retriever_cam | 0.0215 | 0.0006 | 0.0000 | 0.0000 | 0.0223 |
| retriever_cam_scc | 0.0212 | 0.0004 | 0.0849 | 0.0000 | 0.1066 |
| full_contextos | 0.0219 | 0.0004 | 0.0837 | 0.0016 | 0.1075 |

---

## Conversation Size: 250 messages

### Component Ablation

| Pipeline | Prompt Tokens | Token Reduction % | Fact Retention % | Total Latency (s) |
|---|---|---|---|---|
| baseline | 4316.0 | 0.00% | 100.00% | 0.0001 |
| retriever | 5151.0 | 0.00% | 100.00% | 0.0267 |
| retriever_cam | 5151.0 | 0.00% | 100.00% | 0.0289 |
| retriever_cam_scc | 4459.0 | 0.00% | 100.00% | 0.1514 |
| full_contextos | 1680.0 | 61.08% | 100.00% | 0.1691 |

### Latency Breakdown

| Pipeline | Retriever (s) | CAM (s) | SCC (s) | APC (s) | Total (s) |
|---|---|---|---|---|---|
| baseline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0001 |
| retriever | 0.0263 | 0.0000 | 0.0000 | 0.0000 | 0.0267 |
| retriever_cam | 0.0278 | 0.0007 | 0.0000 | 0.0000 | 0.0289 |
| retriever_cam_scc | 0.0251 | 0.0006 | 0.1254 | 0.0000 | 0.1514 |
| full_contextos | 0.0241 | 0.0006 | 0.1220 | 0.0223 | 0.1691 |

### SCC Ablation (250 messages)

| SCC Logic | Fact Retention % | Token Reduction % | Total Latency (s) | Selected Candidates |
|---|---|---|---|---|
| Sprint 16 (Query Distance) | 100.00% | 0.00% | 0.0252 | 50.0 |
| Sprint 17 (Cosine Similarity) | 100.00% | 0.00% | 0.1514 | 50.0 |

### Adaptive Retrieval Ablation (250 messages)

| Retrieval Logic | Fact Retention % | Token Reduction % | Total Latency (s) | Retrieved Candidates |
|---|---|---|---|---|
| Fixed top_k=5 | 100.00% | 0.00% | 0.0419 | 5.0 |
| Adaptive Retrieval | 100.00% | 0.00% | 0.1514 | 50.0 |

---
