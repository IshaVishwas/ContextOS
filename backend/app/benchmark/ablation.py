import time
from typing import Dict, Any, List
from app.benchmark.metrics import BenchmarkResult
from app.benchmark.baseline import check_fact_retention, calculate_tokens
from app.db.session import SessionLocal
from app import crud
from app.schemas.conversation import ConversationCreate
from app.schemas.message import MessageCreate
from app.rag.memory_indexer import memory_indexer
from app.models.user import User

from app.evaluation.latency_tracker import Timer
from app.rag.embedding_service import embedding_service
from app.rag.vector_store import vector_store
from app.algorithms.cam.cam_engine import cam_engine
from app.algorithms.scc.compressor import scc_engine
from app.algorithms.apc.prompt_builder import apc_engine

def run_ablation(iteration: int, data: Dict[str, Any], pipeline_type: str, provider_name: str = "gemini") -> BenchmarkResult:
    size = data["size"]
    messages = data["messages"]
    query = data["query"]
    expected_facts = data["expected_facts"]
    
    db = SessionLocal()
    try:
        # User & Conversation Setup
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            user = User(id=1, email="benchmark@test.com", hashed_password="pw", is_active=True, full_name="Bench")
            db.add(user)
            db.commit()
            
        conv_in = ConversationCreate(title=f"Ablation Size {size} Iter {iteration}")
        conv = crud.conversation.create_with_user(db=db, obj_in=conv_in, user_id=user.id)
        
        # Index Messages
        for msg in messages:
            msg_in = MessageCreate(conversation_id=conv.id, role=msg["role"], content=msg["content"])
            db_msg = crud.message.create(db=db, obj_in=msg_in)
            try:
                memory_indexer.index_message(db=db, message_id=db_msg.id)
            except Exception:
                pass 
        
        recent_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
        system_prompt = "You are ContextOS, an advanced AI assistant."

        # Initialize Latencies
        ret_lat = cam_lat = scc_lat = apc_lat = total_lat = 0.0
        retrieval_count = selected_count = 0
        comp_ratio = 1.0

        # Step A: Baseline
        with Timer() as total_timer:
            if pipeline_type == "baseline":
                monolithic_prompt = f"System: {system_prompt}\n"
                for msg in recent_messages:
                    monolithic_prompt += f"{msg['role']}: {msg['content']}\n"
                monolithic_prompt += f"user: {query}"
                opt_prompt = monolithic_prompt
                orig_tokens = comp_tokens = calculate_tokens(opt_prompt)
                
            else:
                # Retriever setup
                with Timer() as retriever_timer:
                    from app.rag.adaptive import AdaptiveRetrievalStrategy
                    strategy = AdaptiveRetrievalStrategy()
                    
                    if pipeline_type == "fixed_top_k":
                        adaptive_k = 5
                    else:
                        adaptive_k = strategy.determine_k(len(recent_messages), query)
                    
                    query_vector = embedding_service.generate_embedding(query)
                    results = vector_store.similarity_search("memories", query_vector, adaptive_k)
                    
                    formatted_results = []
                    if results and results.get('ids') and len(results['ids']) > 0:
                        ids = results['ids'][0]
                        documents = results['documents'][0] if results.get('documents') else []
                        metadatas = results['metadatas'][0] if results.get('metadatas') else []
                        distances = results['distances'][0] if results.get('distances') else []
                        embeddings = results['embeddings'][0] if results.get('embeddings') else []

                        for i in range(len(ids)):
                            formatted_results.append({
                                "id": ids[i],
                                "document": documents[i] if i < len(documents) else "",
                                "metadata": metadatas[i] if i < len(metadatas) else {},
                                "distance": distances[i] if i < len(distances) else 0.0,
                                "embedding": embeddings[i] if i < len(embeddings) else []
                            })
                            
                    if pipeline_type != "fixed_top_k":
                        formatted_results = strategy.filter_candidates(formatted_results)
                
                ret_lat = retriever_timer.duration
                retrieval_count = len(formatted_results)
                
                if pipeline_type == "retriever":
                    # B. Baseline + Retriever
                    raw_context = "\n".join([m.get("document", "") for m in formatted_results])
                    opt_prompt = f"System: {system_prompt}\nContext: {raw_context}\n"
                    for msg in recent_messages:
                        opt_prompt += f"{msg['role']}: {msg['content']}\n"
                    opt_prompt += f"user: {query}"
                    
                    # Estimate original token size as if RAG wasn't used
                    orig_prompt = f"System: {system_prompt}\n"
                    for msg in recent_messages:
                        orig_prompt += f"{msg['role']}: {msg['content']}\n"
                    orig_prompt += f"user: {query}"
                    orig_tokens = calculate_tokens(orig_prompt)
                    comp_tokens = calculate_tokens(opt_prompt)
                    
                else:
                    # Apply CAM
                    with Timer() as cam_timer:
                        ranked_results = cam_engine.rank(raw_memories=formatted_results, query_context={})
                    cam_lat = cam_timer.duration
                    
                    if pipeline_type == "retriever_cam":
                        # C. Retriever + CAM
                        selected_count = len(ranked_results)
                        raw_context = "\n".join([m.get("document", "") for m in ranked_results])
                        opt_prompt = f"System: {system_prompt}\nContext: {raw_context}\n"
                        for msg in recent_messages:
                            opt_prompt += f"{msg['role']}: {msg['content']}\n"
                        opt_prompt += f"user: {query}"
                        
                        orig_prompt = f"System: {system_prompt}\n"
                        for msg in recent_messages:
                            orig_prompt += f"{msg['role']}: {msg['content']}\n"
                        orig_prompt += f"user: {query}"
                        orig_tokens = calculate_tokens(orig_prompt)
                        comp_tokens = calculate_tokens(opt_prompt)
                        
                    else:
                        # Apply SCC
                        with Timer() as scc_timer:
                            if pipeline_type == "scc_query_distance":
                                # Mock Sprint 16 Old Logic (Query Distance)
                                # Simply group all memories whose distance differ by less than 0.2
                                clusters = []
                                used = set()
                                for m in ranked_results:
                                    if m["id"] in used: continue
                                    cluster_docs = [m["document"]]
                                    used.add(m["id"])
                                    for other in ranked_results:
                                        if other["id"] not in used and abs(m["distance"] - other["distance"]) < 0.2:
                                            cluster_docs.append(other["document"])
                                            used.add(other["id"])
                                    # Redundancy filter dropped everything but the lead
                                    clusters.append(f"- {cluster_docs[0]}")
                                compressed_context = "\n".join(clusters)
                                selected_count = len(ranked_results)
                                compressed_count = len(clusters)
                            else:
                                # Normal Sprint 17 Logic
                                scc_result = scc_engine.compress(ranked_results)
                                compressed_context = scc_result.compressed_context
                                selected_count = scc_result.original_memory_count
                                compressed_count = scc_result.compressed_memory_count
                                
                        scc_lat = scc_timer.duration
                        
                        if pipeline_type in ["retriever_cam_scc", "scc_query_distance", "fixed_top_k"]:
                            # D. Retriever + CAM + SCC (No APC)
                            opt_prompt = f"System: {system_prompt}\nContext: {compressed_context}\n"
                            for msg in recent_messages:
                                opt_prompt += f"{msg['role']}: {msg['content']}\n"
                            opt_prompt += f"user: {query}"
                            
                            orig_prompt = f"System: {system_prompt}\n"
                            for msg in recent_messages:
                                orig_prompt += f"{msg['role']}: {msg['content']}\n"
                            orig_prompt += f"user: {query}"
                            orig_tokens = calculate_tokens(orig_prompt)
                            comp_tokens = calculate_tokens(opt_prompt)
                            
                        else:
                            # E. Full ContextOS (APC)
                            with Timer() as apc_timer:
                                apc_result = apc_engine.build_prompt(
                                    user_query=query,
                                    compressed_context=compressed_context,
                                    recent_messages=recent_messages,
                                    system_instructions=system_prompt,
                                    provider=provider_name
                                )
                            apc_lat = apc_timer.duration
                            opt_prompt = apc_result.formatted_prompt
                            
                            orig_prompt = f"System: {system_prompt}\n"
                            for msg in recent_messages:
                                orig_prompt += f"{msg['role']}: {msg['content']}\n"
                            orig_prompt += f"user: {query}"
                            
                            orig_tokens = calculate_tokens(orig_prompt)
                            comp_tokens = calculate_tokens(opt_prompt)

        total_lat = total_timer.duration

        # Fact retention
        retained_facts = check_fact_retention(opt_prompt, expected_facts)
        retention_perc = (retained_facts / len(expected_facts)) * 100.0 if expected_facts else 100.0
        
        token_saved = max(0, orig_tokens - comp_tokens)
        reduction_perc = (token_saved / orig_tokens * 100.0) if orig_tokens else 0.0

        return BenchmarkResult(
            pipeline=pipeline_type,
            conversation_size=size,
            iteration=iteration,
            original_tokens=orig_tokens,
            final_prompt_tokens=comp_tokens,
            token_reduction=token_saved,
            token_reduction_percentage=reduction_perc,
            retrieval_count=retrieval_count,
            selected_memory_count=selected_count,
            compression_ratio=comp_ratio,
            retrieval_latency=ret_lat,
            cam_latency=cam_lat,
            scc_latency=scc_lat,
            apc_latency=apc_lat,
            total_pipeline_latency=total_lat,
            relevant_facts_originally_present=len(expected_facts),
            relevant_facts_retained=retained_facts,
            relevant_fact_retention_percentage=retention_perc,
            irrelevant_information_removed_percentage=reduction_perc
        )
    finally:
        db.close()
