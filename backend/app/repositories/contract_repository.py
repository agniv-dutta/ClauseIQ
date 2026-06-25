from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.contract import Contract
from app.models.clause import Clause
from typing import Optional, List


class ContractRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, contract_id: str) -> Optional[Contract]:
        result = await self.db.execute(select(Contract).where(Contract.id == contract_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> List[Contract]:
        result = await self.db.execute(
            select(Contract).where(Contract.user_id == user_id).order_by(Contract.uploaded_at.desc())
        )
        return result.scalars().all()

    async def create(self, contract: Contract) -> Contract:
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        return contract

    async def update(self, contract: Contract) -> Contract:
        await self.db.commit()
        await self.db.refresh(contract)
        return contract

    async def delete(self, contract_id: str) -> bool:
        result = await self.db.execute(delete(Contract).where(Contract.id == contract_id))
        await self.db.commit()
        return result.rowcount > 0
