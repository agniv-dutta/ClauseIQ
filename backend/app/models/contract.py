import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ContractType(str, enum.Enum):
    SAAS_AGREEMENT = "SAAS_AGREEMENT"
    NDA = "NDA"
    VENDOR_AGREEMENT = "VENDOR_AGREEMENT"
    EMPLOYMENT = "EMPLOYMENT"
    LEASE = "LEASE"
    OTHER = "OTHER"


class ContractStatus(str, enum.Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    ANALYZED = "ANALYZED"
    FAILED = "FAILED"


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[uuid.UUID] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    contract_type: Mapped[ContractType] = mapped_column(
        SQLEnum(ContractType), default=ContractType.OTHER, nullable=False
    )
    status: Mapped[ContractStatus] = mapped_column(
        SQLEnum(ContractStatus), default=ContractStatus.UPLOADED, nullable=False
    )
    raw_text: Mapped[str] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    clauses = relationship("Clause", back_populates="contract", cascade="all, delete-orphan")
    analysis = relationship("Analysis", back_populates="contract", uselist=False, cascade="all, delete-orphan")
