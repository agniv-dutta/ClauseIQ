# ClauseIQ Backend

AI-powered contract intelligence platform backend built with FastAPI, PostgreSQL, and Google Gemini.

## Features

- **User Authentication**: JWT-based auth with secure password hashing
- **Contract Upload**: Support for PDF and DOCX file uploads with validation
- **Document Parsing**: Multi-layer text extraction (pdfplumber, PyMuPDF, OCR fallback)
- **Clause Segmentation**: Hybrid regex/LLM-based clause extraction
- **AI Analysis**: Gemini-powered risk assessment and clause classification
- **Market Benchmarking**: ChromaDB-powered similarity search against market standards
- **Risk Scoring**: Weighted risk scoring algorithm with detailed explanations
- **Report Generation**: PDF export with executive summaries and negotiation suggestions
- **Rate Limiting**: In-memory rate limiting for critical endpoints

## Tech Stack

- **Framework**: FastAPI (latest stable)
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **ORM**: SQLAlchemy with asyncpg driver
- **Migrations**: Alembic
- **Authentication**: python-jose (JWT) + passlib (bcrypt)
- **Document Parsing**: pdfplumber, PyMuPDF, pytesseract, python-docx
- **AI/LLM**: Google Gemini API
- **Vector DB**: ChromaDB
- **Report Generation**: ReportLab
- **Testing**: pytest + httpx

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app instantiation
│   ├── config.py                  # Pydantic Settings
│   ├── database.py                # Async engine, session factory
│   ├── dependencies.py            # FastAPI Depends()
│   ├── models/                    # SQLAlchemy models
│   ├── schemas/                   # Pydantic schemas
│   ├── routers/                   # API endpoints
│   ├── services/                  # Business logic
│   ├── repositories/              # DB CRUD operations
│   └── utils/                     # Utilities (exceptions, logging)
├── alembic/                       # Migration scripts
├── tests/                         # Test suite
├── seed_data/                     # Market standard clauses
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or SQLite for local dev)
- Tesseract OCR (for PDF text extraction)
- Google Gemini API key

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required variables:
   - `DATABASE_URL`: PostgreSQL connection string (or set `USE_SQLITE=True`)
   - `SECRET_KEY`: JWT secret key (min 32 characters)
   - `GEMINI_API_KEY`: Google Gemini API key
   - `CORS_ORIGINS`: Frontend URL (default: http://localhost:5173)

5. **Run database migrations**
   ```bash
   python -m alembic upgrade head
   ```

6. **Seed market standard clauses**
   ```bash
   python seed_data/seed_db.py
   ```

7. **Run the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run with docker-compose**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Start PostgreSQL database
   - Build and start the backend service
   - Run migrations automatically
   - Seed market standard clauses

2. **Access the API**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user info (requires auth)

### Contracts

- `POST /contracts/upload` - Upload a contract file
- `GET /contracts/` - List all contracts for current user
- `GET /contracts/{id}` - Get specific contract details
- `DELETE /contracts/{id}` - Delete a contract

### Analysis

- `POST /contracts/{id}/analyze` - Trigger contract analysis (background task)
- `GET /contracts/{id}/analysis` - Get analysis results
- `GET /contracts/{id}/report` - Download PDF report

### Health

- `GET /health` - Health check endpoint

## Database Migrations

### Create a new migration
```bash
python -m alembic revision --autogenerate -m "description"
```

### Apply migrations
```bash
python -m alembic upgrade head
```

### Rollback migrations
```bash
python -m alembic downgrade -1
```

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Tests include:
- Authentication flow (register, login, token validation)
- Contract upload, listing, retrieval, and deletion
- AI service with mocked LLM responses

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `USE_SQLITE` | Use SQLite instead of PostgreSQL | False |
| `SECRET_KEY` | JWT secret key | - |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `GEMINI_MODEL` | Gemini model name | gemini-1.5-pro |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:5173 |
| `MAX_UPLOAD_SIZE` | Max file upload size (bytes) | 10485760 (10MB) |
| `UPLOAD_DIR` | Directory for uploaded files | uploads |
| `CHROMA_PERSIST_DIR` | ChromaDB storage directory | chroma_db |
| `RATE_LIMIT_REQUESTS` | Rate limit requests per period | 10 |
| `RATE_LIMIT_PERIOD` | Rate limit period (seconds) | 60 |

## Production Considerations

### Security

- Change `SECRET_KEY` to a strong, random value
- Use HTTPS in production
- Implement proper rate limiting with Redis
- Add request signing for sensitive operations
- Implement proper logging and monitoring

### Performance

- Use Celery/RQ for background tasks instead of FastAPI BackgroundTasks
- Implement Redis caching for LLM responses
- Add database connection pooling
- Implement proper indexing on frequently queried columns

### Scalability

- Use a production-grade message queue (RabbitMQ, Redis)
- Implement horizontal scaling with load balancer
- Use CDN for static file serving
- Consider microservices architecture for AI processing

## Troubleshooting

### OCR Issues

If Tesseract OCR fails:
- Ensure Tesseract is installed: `tesseract --version`
- Install language packs: `apt-get install tesseract-ocr-eng`
- Check Tesseract data path in environment

### Database Connection Issues

- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database exists: `createdb clauseiq`
- For SQLite, ensure `USE_SQLITE=True`

### AI Service Issues

- Verify GEMINI_API_KEY is valid
- Check API quota limits
- Review logs for specific error messages
- Test API key with curl or Postman

## License

Proprietary - All rights reserved

## Support

For issues and questions, contact the development team.
