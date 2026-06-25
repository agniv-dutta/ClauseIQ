import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.services.auth_service import get_password_hash
import io


# Use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def auth_token(client: AsyncClient):
    # Create a test user
    async with TestingSessionLocal() as session:
        user = User(
            email="test@example.com",
            hashed_password=get_password_hash("testpassword123"),
            company_name="Test Company"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    # Login to get token
    response = await client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_upload_contract_pdf(client: AsyncClient, auth_token: str):
    # Create a simple PDF file
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"
    
    response = await client.post(
        "/contracts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] == "UPLOADED"


@pytest.mark.asyncio
async def test_upload_contract_docx(client: AsyncClient, auth_token: str):
    # Create a simple DOCX file (minimal valid structure)
    docx_content = b"PK\x03\x04" + b"\x00" * 100  # Minimal ZIP header for DOCX
    
    response = await client.post(
        "/contracts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test.docx", io.BytesIO(docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_upload_invalid_file_type(client: AsyncClient, auth_token: str):
    response = await client.post(
        "/contracts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_empty_file(client: AsyncClient, auth_token: str):
    response = await client.post(
        "/contracts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test.pdf", io.BytesIO(b""), "application/pdf")}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_contracts(client: AsyncClient, auth_token: str):
    # Upload a contract first
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"
    await client.post(
        "/contracts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    )
    
    # List contracts
    response = await client.get(
        "/contracts/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_contract(client: AsyncClient, auth_token: str):
    # Upload a contract first
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"
    upload_response = await client.post(
        "/contracts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    )
    contract_id = upload_response.json()["id"]
    
    # Get contract
    response = await client.get(
        f"/contracts/{contract_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contract_id


@pytest.mark.asyncio
async def test_delete_contract(client: AsyncClient, auth_token: str):
    # Upload a contract first
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"
    upload_response = await client.post(
        "/contracts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    )
    contract_id = upload_response.json()["id"]
    
    # Delete contract
    response = await client.delete(
        f"/contracts/{contract_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_contract_access_denied(client: AsyncClient, auth_token: str):
    # Create another user
    async with TestingSessionLocal() as session:
        user2 = User(
            email="other@example.com",
            hashed_password=get_password_hash("password123"),
            company_name="Other Company"
        )
        session.add(user2)
        await session.commit()
    
    # Upload contract as first user
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n%%EOF"
    upload_response = await client.post(
        "/contracts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    )
    contract_id = upload_response.json()["id"]
    
    # Try to access as second user
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "other@example.com",
            "password": "password123"
        }
    )
    token2 = login_response.json()["access_token"]
    
    response = await client.get(
        f"/contracts/{contract_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 403
