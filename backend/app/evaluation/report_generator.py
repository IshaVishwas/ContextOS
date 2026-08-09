from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.evaluation import EvaluationRun
from typing import Dict, Any

class ReportGenerator:
    def generate_stats(self, db: Session) -> Dict[str, Any]:
        """
        Generates a charts-ready JSON payload aggregating all evaluation runs.
        """
        total_runs = db.query(EvaluationRun).count()
        if total_runs == 0:
            return {"status": "no_data"}
            
        avg_compression_ratio = db.query(func.avg(EvaluationRun.compression_ratio)).scalar() or 0.0
        avg_tokens_saved = db.query(func.avg(EvaluationRun.token_saved)).scalar() or 0.0
        
        avg_latencies = db.query(
            func.avg(EvaluationRun.retriever_latency),
            func.avg(EvaluationRun.cam_latency),
            func.avg(EvaluationRun.scc_latency),
            func.avg(EvaluationRun.apc_latency),
            func.avg(EvaluationRun.llm_latency),
            func.avg(EvaluationRun.total_latency),
        ).first()

        provider_distribution_raw = db.query(EvaluationRun.provider, func.count(EvaluationRun.id)).group_by(EvaluationRun.provider).all()
        provider_distribution = {p: c for p, c in provider_distribution_raw}

        return {
            "total_runs": total_runs,
            "averages": {
                "compression_ratio": round(avg_compression_ratio, 4),
                "tokens_saved_per_turn": round(avg_tokens_saved, 2),
                "latency_ms": {
                    "retriever": round((avg_latencies[0] or 0) * 1000, 2),
                    "cam": round((avg_latencies[1] or 0) * 1000, 2),
                    "scc": round((avg_latencies[2] or 0) * 1000, 2),
                    "apc": round((avg_latencies[3] or 0) * 1000, 2),
                    "llm": round((avg_latencies[4] or 0) * 1000, 2),
                    "total": round((avg_latencies[5] or 0) * 1000, 2),
                }
            },
            "provider_distribution": provider_distribution
        }

report_generator = ReportGenerator()
