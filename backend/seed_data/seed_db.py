import asyncio
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine, Base
from app.models.market_standard import MarketStandardClause
from app.models.market_standard import ContractType, ClauseType
from app.services.benchmark_service import benchmark_service
from app.utils.logging_config import logger


async def seed_market_standard_clauses():
    """Seed market standard clauses into database and ChromaDB."""
    
    # Load seed data from JSON
    seed_file = os.path.join(os.path.dirname(__file__), "market_standard_clauses.json")
    
    with open(seed_file, 'r') as f:
        seed_data = json.load(f)
    
    clauses = seed_data.get('market_standard_clauses', [])
    
    async with AsyncSessionLocal() as session:
        try:
            # Clear existing data
            await session.execute("DELETE FROM market_standard_clauses")
            await session.commit()
            
            # Clear ChromaDB collection
            benchmark_service.clear_collection()
            
            # Add new clauses
            for clause_data in clauses:
                # Create database record
                contract_type = ContractType(clause_data['contract_type'])
                clause_type = ClauseType(clause_data['clause_type'])
                
                db_clause = MarketStandardClause(
                    contract_type=contract_type,
                    clause_type=clause_type,
                    standard_text=clause_data['standard_text']
                )
                
                session.add(db_clause)
                await session.flush()
                
                # Add to ChromaDB
                benchmark_service.add_market_standard_clause(
                    clause_id=db_clause.id,
                    contract_type=contract_type,
                    clause_type=clause_type,
                    standard_text=clause_data['standard_text']
                )
            
            await session.commit()
            logger.info(f"Successfully seeded {len(clauses)} market standard clauses")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to seed market standard clauses: {e}")
            raise


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def main():
    """Main seeding function."""
    logger.info("Starting database seeding...")
    
    # Create tables
    await create_tables()
    
    # Seed market standard clauses
    await seed_market_standard_clauses()
    
    logger.info("Database seeding completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
