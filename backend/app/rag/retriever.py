from typing import List, Dict, Any, Optional
from app.rag.embedding_service import embedding_service
from app.rag.vector_store import vector_store
from app.evaluation.latency_tracker import Timer

class Retriever:
    def __init__(self, collection_name: str = "memories"):
        self.collection_name = collection_name

    def semantic_search(
        self, 
        query: str, 
        top_k: Optional[int] = None, 
        metadata_filter: Optional[Dict[str, Any]] = None,
        similarity_threshold: float = 0.0, # Placeholder for threshold logic if needed
        conversation_size: int = 0
    ) -> Dict[str, Any]:
        with Timer() as retriever_timer:
            from app.rag.adaptive import AdaptiveRetrievalStrategy
            strategy = AdaptiveRetrievalStrategy()
            
            # 1. Determine adaptive k
            adaptive_k = top_k if top_k is not None else strategy.determine_k(conversation_size, query)
            
            # Generate query embedding
            query_vector = embedding_service.generate_embedding(query)

            # Search ChromaDB
            results = vector_store.similarity_search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                top_k=adaptive_k,
                metadata_filter=metadata_filter
            )

            formatted_results = []
            if results and results.get('ids') and len(results['ids']) > 0:
                ids = results['ids'][0]
                documents = results['documents'][0] if results.get('documents') else []
                metadatas = results['metadatas'][0] if results.get('metadatas') else []
                distances = results['distances'][0] if results.get('distances') else []
                embeddings = results['embeddings'][0] if results.get('embeddings') else []

                for i in range(len(ids)):
                    distance = distances[i] if i < len(distances) else 0.0
                    embedding = embeddings[i] if i < len(embeddings) else []
                    formatted_results.append({
                        "id": ids[i],
                        "document": documents[i] if i < len(documents) else "",
                        "metadata": metadatas[i] if i < len(metadatas) else {},
                        "distance": distance,
                        "embedding": embedding
                    })

            # 2. Filter outliers statistically (only if adaptive was used)
            if top_k is None:
                formatted_results = strategy.filter_candidates(formatted_results)

        # Apply Context Allocation Manager (CAM) ranking
        with Timer() as cam_timer:
            from app.algorithms.cam.cam_engine import cam_engine
            
            # We can pass metadata_filter as the query_context for the conversation dependency scorer
            query_context = metadata_filter or {}
            ranked_results = cam_engine.rank(raw_memories=formatted_results, query_context=query_context)

        # Apply Semantic Context Compressor (SCC)
        with Timer() as scc_timer:
            from app.algorithms.scc.compressor import scc_engine
            
            # SCC accepts the ranked memories and outputs a CompressedContextResult
            compressed_result = scc_engine.compress(ranked_results)

        # Return both the ranked list and the compressed context for the caller
        return {
            "ranked_results": ranked_results,
            "scc_result": compressed_result.model_dump(),
            "latencies": {
                "retriever_latency": retriever_timer.duration,
                "cam_latency": cam_timer.duration,
                "scc_latency": scc_timer.duration
            }
        }

retriever = Retriever()
