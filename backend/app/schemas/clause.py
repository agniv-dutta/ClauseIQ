from pydantic import BaseModel
from app.models.clause import ClauseType, RiskLevel


class ClauseRead(BaseModel):
    id: str
    contract_id: str
    clause_type: ClauseType
    extracted_text: str
    position_start: int
    position_end: int
    risk_level: RiskLevel
    risk_explanation: Optional[str] = None
    market_standard_comparison: Optional[str] = None
    negotiation_suggestion: Optional[str] = None

    class Config:
        from_attributes = True


class ClauseRiskFlag(BaseModel):
    clause_id: str
    clause_type: ClauseType
    risk_level: RiskLevel
    risk_explanation: str
    extracted_text: str
