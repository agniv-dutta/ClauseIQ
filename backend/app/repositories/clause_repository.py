from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.clause import Clause
from app.models.clause import RiskLevel
from typing import List, Optional


class ClauseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_contract_id(self, contract_id: str) -> List[Clause]:
        result = await self.db.execute(
            select(Clause)
            .where(Clause.contract_id == contract_id)
            .order_by(Clause.risk_level.desc(), Clause.position_start.asc())
        )
        return result.scalars().all()

    async def create(self, clause: Clause) -> Clause:
        self.db.add(clause)
        await self.db.commit()
        await self.db.refresh(clause)
        return clause

    async def create_bulk(self, clauses: List[Clause]) -> List[Clause]:
        self.db.add_all(clauses)
        await self.db.commit()
        for clause in clauses:
            await self.db.refresh(clause)
        return clauses

    async def get_by_id(self, clause_id: str) -> Optional[Clause]:
        result = await self.db.execute(select(Clause).where(Clause.id == clause_id))
        return result.scalar_one_or_none()
