from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.evaluation import EvaluationRun
from app.evaluation.report_generator import report_generator
from app.schemas.evaluation import EvaluationRun as EvaluationRunSchema
from typing import Any, List

router = APIRouter()

@router.get("/", response_model=List[EvaluationRunSchema])
def list_evaluations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(deps.get_db), 
    current_user = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Retrieve a list of evaluation runs.
    """
    runs = db.query(EvaluationRun).order_by(EvaluationRun.timestamp.desc()).offset(skip).limit(limit).all()
    return runs

@router.get("/latest", response_model=EvaluationRunSchema)
def get_latest_evaluation(
    db: Session = Depends(deps.get_db), 
    current_user = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Retrieve the most recent evaluation run.
    """
    latest_run = db.query(EvaluationRun).order_by(EvaluationRun.timestamp.desc()).first()
    if not latest_run:
        raise HTTPException(status_code=404, detail="No evaluation runs found")
    return latest_run

@router.get("/stats")
def get_evaluation_stats(
    db: Session = Depends(deps.get_db), 
    current_user = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Generate aggregate statistics across all evaluations for reporting/charts.
    """
    try:
        stats = report_generator.generate_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}", response_model=EvaluationRunSchema)
def get_evaluation_by_id(
    id: int, 
    db: Session = Depends(deps.get_db), 
    current_user = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Retrieve an evaluation run by ID.
    """
    run = db.query(EvaluationRun).filter(EvaluationRun.id == id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")
    return run
