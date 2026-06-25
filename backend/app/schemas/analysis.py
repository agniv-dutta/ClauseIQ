from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.schemas.clause import ClauseRead


class AnalysisResult(BaseModel):
    id: str
    contract_id: str
    overall_risk_score: int
    executive_summary: Optional[str] = None
    high_risk_clause_count: int
    medium_risk_clause_count: int
    key_dates: Optional[dict] = None
    key_parties: Optional[dict] = None
    completed_at: datetime
    clauses: List[ClauseRead]

    class Config:
        from_attributes = True


class ExecutiveSummary(BaseModel):
    summary: str
    overall_risk_score: int
    high_risk_count: int
    medium_risk_count: int
