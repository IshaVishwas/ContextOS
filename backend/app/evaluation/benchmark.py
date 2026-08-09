from sqlalchemy.orm import Session
from app.crud.crud_evaluation import evaluation_run
from app.schemas.evaluation import EvaluationRunCreate
from app.evaluation.metrics import EvaluationMetrics

class EvaluationManager:
    def save_evaluation_run(self, db: Session, metrics: EvaluationMetrics) -> int:
        """
        Takes raw metrics, formats them to the schema, and saves to the database.
        Returns the evaluation_id.
        """
        run_create = EvaluationRunCreate(
            query=metrics.query,
            provider=metrics.provider,
            conversation_id=metrics.conversation_id,
            retrieved_memories=metrics.retrieved_memories,
            selected_memories=metrics.selected_memories,
            compression_ratio=metrics.compression_ratio,
            original_tokens=metrics.original_tokens,
            compressed_tokens=metrics.compressed_tokens,
            token_saved=metrics.token_saved,
            retriever_latency=metrics.retriever_latency,
            cam_latency=metrics.cam_latency,
            scc_latency=metrics.scc_latency,
            apc_latency=metrics.apc_latency,
            llm_latency=metrics.llm_latency,
            total_latency=metrics.total_latency
        )
        saved_run = evaluation_run.create(db=db, obj_in=run_create)
        return saved_run.id

benchmark_manager = EvaluationManager()
