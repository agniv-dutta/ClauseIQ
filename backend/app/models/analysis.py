import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    contract_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("contracts.id"), nullable=False, unique=True, index=True
    )
    overall_risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=True)
    high_risk_clause_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    medium_risk_clause_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    key_dates: Mapped[dict] = mapped_column(JSON, nullable=True)
    key_parties: Mapped[dict] = mapped_column(JSON, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    contract = relationship("Contract", back_populates="analysis")
