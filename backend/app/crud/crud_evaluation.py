from app.crud.base import CRUDBase
from app.models.evaluation import EvaluationRun
from app.schemas.evaluation import EvaluationRunCreate, EvaluationRunUpdate

class CRUDEvaluationRun(CRUDBase[EvaluationRun, EvaluationRunCreate, EvaluationRunUpdate]):
    pass

evaluation_run = CRUDEvaluationRun(EvaluationRun)
