import uuid
import enum
from sqlalchemy import String, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ContractType(str, enum.Enum):
    SAAS_AGREEMENT = "SAAS_AGREEMENT"
    NDA = "NDA"
    VENDOR_AGREEMENT = "VENDOR_AGREEMENT"
    EMPLOYMENT = "EMPLOYMENT"
    LEASE = "LEASE"
    OTHER = "OTHER"


class ClauseType(str, enum.Enum):
    PRICING = "PRICING"
    TERM_TERMINATION = "TERM_TERMINATION"
    LIABILITY = "LIABILITY"
    INDEMNIFICATION = "INDEMNIFICATION"
    IP_OWNERSHIP = "IP_OWNERSHIP"
    CONFIDENTIALITY = "CONFIDENTIALITY"
    AUTO_RENEWAL = "AUTO_RENEWAL"
    GOVERNING_LAW = "GOVERNING_LAW"
    LIMITATION_OF_LIABILITY = "LIMITATION_OF_LIABILITY"
    OTHER = "OTHER"


class MarketStandardClause(Base):
    __tablename__ = "market_standard_clauses"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    contract_type: Mapped[ContractType] = mapped_column(
        SQLEnum(ContractType), nullable=False
    )
    clause_type: Mapped[ClauseType] = mapped_column(
        SQLEnum(ClauseType), nullable=False
    )
    standard_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Note: embedding is stored in ChromaDB, referenced by this row's id
