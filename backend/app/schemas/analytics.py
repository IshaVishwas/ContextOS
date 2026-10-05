from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AnalyticsBase(BaseModel):
    total_messages: Optional[int] = 0
    total_tokens: Optional[int] = 0
    compression_saved: Optional[int] = 0
    retrieval_count: Optional[int] = 0

class AnalyticsCreate(AnalyticsBase):
    user_id: int

class AnalyticsUpdate(AnalyticsBase):
    pass

class AnalyticsInDBBase(AnalyticsBase):
    id: int
    user_id: int
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Analytics(AnalyticsInDBBase):
    pass
