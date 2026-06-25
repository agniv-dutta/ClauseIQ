import uuid
import enum
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


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


class RiskLevel(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"


class Clause(Base):
    __tablename__ = "clauses"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    contract_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("contracts.id"), nullable=False, index=True
    )
    clause_type: Mapped[ClauseType] = mapped_column(
        SQLEnum(ClauseType), default=ClauseType.OTHER, nullable=False
    )
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    position_start: Mapped[int] = mapped_column(Integer, nullable=False)
    position_end: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        SQLEnum(RiskLevel), default=RiskLevel.NONE, nullable=False
    )
    risk_explanation: Mapped[str] = mapped_column(Text, nullable=True)
    market_standard_comparison: Mapped[str] = mapped_column(Text, nullable=True)
    negotiation_suggestion: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    contract = relationship("Contract", back_populates="clauses")
