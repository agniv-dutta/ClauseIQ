import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.models.contract import Contract, ContractStatus
from app.schemas.contract import ContractCreate, ContractRead, ContractListItem
from app.dependencies import get_current_user
from app.repositories.contract_repository import ContractRepository
from app.utils.exceptions import BadRequestException, NotFoundException
from app.utils.logging_config import logger
from app.config import settings

router = APIRouter(prefix="/contracts", tags=["contracts"])

# Simple in-memory rate limiter (for hackathon scope)
rate_limit_tracker = {}


def check_rate_limit(user_id: str, endpoint: str):
    """Check if user has exceeded rate limit for an endpoint."""
    import time
    current_time = time.time()
    key = f"{user_id}:{endpoint}"
    
    if key in rate_limit_tracker:
        requests = rate_limit_tracker[key]
        # Remove requests older than the rate limit period
        requests = [t for t in requests if current_time - t < settings.RATE_LIMIT_PERIOD]
        
        if len(requests) >= settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded for {endpoint}"
            )
        
        requests.append(current_time)
        rate_limit_tracker[key] = requests
    else:
        rate_limit_tracker[key] = [current_time]


@router.post("/upload", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
async def upload_contract(
    file: UploadFile = File(...),
    contract_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a contract file (PDF or DOCX)."""
    # Rate limit
    check_rate_limit(current_user.id, "upload")
    
    # Validate file type
    if file.filename.lower().endswith('.pdf'):
        file_type = 'pdf'
    elif file.filename.lower().endswith('.docx'):
        file_type = 'docx'
    else:
        raise BadRequestException("Only PDF and DOCX files are allowed")
    
    # Validate file size
    content = await file.read()
    if len(content) == 0:
        raise BadRequestException("File is empty")
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException(f"File size exceeds maximum of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB")
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(upload_dir, f"{file_id}{file_extension}")
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create contract record
    contract_repo = ContractRepository(db)
    
    # Map string to enum if provided
    from app.models.contract import ContractType
    contract_type_enum = None
    if contract_type:
        try:
            contract_type_enum = ContractType(contract_type.upper())
        except ValueError:
            pass
    
    contract = Contract(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        contract_type=contract_type_enum or ContractType.OTHER,
        status=ContractStatus.UPLOADED
    )
    
    created_contract = await contract_repo.create(contract)
    logger.info(f"Contract uploaded: {created_contract.id} by user {current_user.id}")
    
    return created_contract


@router.get("/", response_model=list[ContractListItem])
async def list_contracts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all contracts for the current user."""
    contract_repo = ContractRepository(db)
    contracts = await contract_repo.get_by_user_id(current_user.id)
    return contracts


@router.get("/{contract_id}", response_model=ContractRead)
async def get_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific contract by ID."""
    contract_repo = ContractRepository(db)
    contract = await contract_repo.get_by_id(contract_id)
    
    if not contract:
        raise NotFoundException("Contract not found")
    
    if contract.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return contract


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a contract by ID."""
    contract_repo = ContractRepository(db)
    contract = await contract_repo.get_by_id(contract_id)
    
    if not contract:
        raise NotFoundException("Contract not found")
    
    if contract.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Delete file from disk
    try:
        if os.path.exists(contract.file_path):
            os.remove(contract.file_path)
    except Exception as e:
        logger.warning(f"Failed to delete file {contract.file_path}: {e}")
    
    # Delete from database
    await contract_repo.delete(contract_id)
    logger.info(f"Contract deleted: {contract_id} by user {current_user.id}")
