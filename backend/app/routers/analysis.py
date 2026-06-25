from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.contract import Contract, ContractStatus
from app.models.clause import Clause, ClauseType, RiskLevel
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResult
from app.dependencies import get_current_user
from app.repositories.contract_repository import ContractRepository
from app.repositories.clause_repository import ClauseRepository
from app.services.document_parser import DocumentParser
from app.services.clause_segmenter import ClauseSegmenter
from app.services.ai_service import ai_service
from app.services.risk_scorer import RiskScorer
from app.services.benchmark_service import benchmark_service
from app.utils.exceptions import NotFoundException, BadRequestException
from app.utils.logging_config import logger
from datetime import datetime, timezone
from typing import Dict, Any

router = APIRouter(prefix="/contracts", tags=["analysis"])


async def analyze_contract_task(contract_id: str, db: AsyncSession):
    """Background task to analyze a contract."""
    try:
        # Get contract
        result = await db.execute(select(Contract).where(Contract.id == contract_id))
        contract = result.scalar_one_or_none()
        
        if not contract:
            logger.error(f"Contract {contract_id} not found for analysis")
            return
        
        # Set status to PROCESSING
        contract.status = ContractStatus.PROCESSING
        await db.commit()
        
        # Extract text from document
        file_type = "pdf" if contract.filename.lower().endswith('.pdf') else "docx"
        raw_text, page_count = DocumentParser.extract_text(contract.file_path, file_type)
        
        if not raw_text:
            contract.status = ContractStatus.FAILED
            await db.commit()
            logger.error(f"Failed to extract text from contract {contract_id}")
            return
        
        # Save raw text
        contract.raw_text = raw_text
        await db.commit()
        
        # Segment text into clauses
        clause_segments = ClauseSegmenter.segment(raw_text)
        
        # Process each clause
        clause_repo = ClauseRepository(db)
        clauses_data = []
        
        for clause_text, start, end in clause_segments:
            # Classify clause type
            clause_type = await ai_service.classify_clause(clause_text)
            
            # Assess risk
            risk_level, risk_explanation = await ai_service.assess_risk(clause_text, clause_type)
            
            # Get market standard comparison
            market_comparison = benchmark_service.generate_comparison(clause_text, clause_type)
            
            # Suggest negotiation if high/medium risk
            negotiation_suggestion = None
            if risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
                negotiation_suggestion = await ai_service.suggest_negotiation(
                    clause_text, clause_type, risk_explanation
                )
            
            # Create clause object
            clause = Clause(
                contract_id=contract.id,
                clause_type=clause_type,
                extracted_text=clause_text,
                position_start=start,
                position_end=end,
                risk_level=risk_level,
                risk_explanation=risk_explanation,
                market_standard_comparison=market_comparison,
                negotiation_suggestion=negotiation_suggestion
            )
            
            clauses_data.append({
                "clause_type": clause_type,
                "risk_level": risk_level,
                "risk_explanation": risk_explanation
            })
            
            await clause_repo.create(clause)
        
        # Compute overall risk score
        overall_risk_score = RiskScorer.compute_overall_risk_score(clauses_data)
        high_risk_count, medium_risk_count, _ = RiskScorer.count_risks(clauses_data)
        
        # Generate executive summary
        executive_summary = await ai_service.generate_summary(clauses_data, overall_risk_score)
        
        # Create analysis record
        analysis = Analysis(
            contract_id=contract.id,
            overall_risk_score=overall_risk_score,
            executive_summary=executive_summary,
            high_risk_clause_count=high_risk_count,
            medium_risk_clause_count=medium_risk_count,
            key_dates={},  # Would be populated by date extraction
            key_parties={}  # Would be populated by party extraction
        )
        
        db.add(analysis)
        
        # Update contract status
        contract.status = ContractStatus.ANALYZED
        contract.analyzed_at = datetime.now(timezone.utc)
        
        await db.commit()
        logger.info(f"Contract analysis completed: {contract_id}")
        
    except Exception as e:
        logger.error(f"Contract analysis failed for {contract_id}: {e}")
        # Set status to FAILED
        result = await db.execute(select(Contract).where(Contract.id == contract_id))
        contract = result.scalar_one_or_none()
        if contract:
            contract.status = ContractStatus.FAILED
            await db.commit()


@router.post("/{contract_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_contract(
    contract_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger analysis of a contract (runs in background)."""
    # Rate limit
    from app.routers.contracts import check_rate_limit
    check_rate_limit(current_user.id, "analyze")
    
    # Get contract
    contract_repo = ContractRepository(db)
    contract = await contract_repo.get_by_id(contract_id)
    
    if not contract:
        raise NotFoundException("Contract not found")
    
    if contract.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if contract.status == ContractStatus.PROCESSING:
        raise BadRequestException("Contract is already being analyzed")
    
    if contract.status == ContractStatus.ANALYZED:
        raise BadRequestException("Contract has already been analyzed")
    
    # Add background task
    background_tasks.add_task(analyze_contract_task, contract_id, db)
    
    return {"message": "Analysis started", "contract_id": contract_id}


@router.get("/{contract_id}/analysis", response_model=AnalysisResult)
async def get_analysis(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the analysis results for a contract."""
    # Get contract
    contract_repo = ContractRepository(db)
    contract = await contract_repo.get_by_id(contract_id)
    
    if not contract:
        raise NotFoundException("Contract not found")
    
    if contract.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if contract.status != ContractStatus.ANALYZED:
        raise BadRequestException("Contract has not been analyzed yet")
    
    # Get analysis
    result = await db.execute(select(Analysis).where(Analysis.contract_id == contract_id))
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise NotFoundException("Analysis not found")
    
    # Get clauses
    clause_repo = ClauseRepository(db)
    clauses = await clause_repo.get_by_contract_id(contract_id)
    
    # Build response
    return AnalysisResult(
        id=analysis.id,
        contract_id=analysis.contract_id,
        overall_risk_score=analysis.overall_risk_score,
        executive_summary=analysis.executive_summary,
        high_risk_clause_count=analysis.high_risk_clause_count,
        medium_risk_clause_count=analysis.medium_risk_clause_count,
        key_dates=analysis.key_dates,
        key_parties=analysis.key_parties,
        completed_at=analysis.completed_at,
        clauses=clauses
    )


@router.get("/{contract_id}/report")
async def get_report(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate and download a PDF report for the contract analysis."""
    # Get contract
    contract_repo = ContractRepository(db)
    contract = await contract_repo.get_by_id(contract_id)
    
    if not contract:
        raise NotFoundException("Contract not found")
    
    if contract.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if contract.status != ContractStatus.ANALYZED:
        raise BadRequestException("Contract has not been analyzed yet")
    
    # Get analysis and clauses
    result = await db.execute(select(Analysis).where(Analysis.contract_id == contract_id))
    analysis = result.scalar_one_or_none()
    
    clause_repo = ClauseRepository(db)
    clauses = await clause_repo.get_by_contract_id(contract_id)
    
    # Generate PDF report
    from app.services.report_generator import ReportGenerator
    from fastapi.responses import StreamingResponse
    import io
    
    generator = ReportGenerator()
    pdf_bytes = generator.generate_report(contract, analysis, clauses)
    
    # Return as streaming response
    pdf_stream = io.BytesIO(pdf_bytes)
    
    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={contract.filename}_report.pdf"
        }
    )
