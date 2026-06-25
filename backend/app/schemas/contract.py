from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.contract import ContractType, ContractStatus


class ContractCreate(BaseModel):
    filename: str
    contract_type: Optional[ContractType] = None


class ContractRead(BaseModel):
    id: str
    user_id: str
    filename: str
    file_path: str
    contract_type: ContractType
    status: ContractStatus
    raw_text: Optional[str] = None
    uploaded_at: datetime
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ContractListItem(BaseModel):
    id: str
    filename: str
    contract_type: ContractType
    status: ContractStatus
    uploaded_at: datetime
    analyzed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
