# DocFlow AI - Intelligent Transport Document Processing Platform

A production-quality full-stack system for ingesting logistics documents (PDF/images), extracting structured data, validating it, enabling human correction, and integrating results into downstream workflows.

## Architecture

The system follows **Hexagonal Architecture** with clear separation between:
- **Domain Layer**: Core business logic, entities, value objects
- **Application Layer**: Use cases and orchestration
- **Infrastructure Layer**: External services (OCR, LLM, Storage, Database)
- **API Layer**: REST endpoints and middleware

## Tech Stack

- **Frontend**: React + TypeScript
- **Backend**: Python FastAPI
- **OCR**: PaddleOCR / Tesseract (pluggable)
- **LLM**: OpenAI / Ollama (pluggable)
- **Database**: PostgreSQL
- **Storage**: S3-compatible (MinIO for local dev)
- **Messaging**: Redis / RabbitMQ
- **Auth**: JWT-based with RBAC

## Features

- Document upload (PDF, images)
- OCR + layout-aware text extraction
- Structured field extraction with confidence scoring
- Validation rules engine
- Human-in-the-loop correction UI
- Export to TMS API
- Audit trail and versioning
- Comprehensive error handling and retries
- Monitoring and observability

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DocFlow-AI
   ```

2. **Configure environment variables**
   - Copy `.env.example` to `.env` (if it exists) or set environment variables
   - Configure database, storage, and API keys

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```
   This starts:
   - PostgreSQL database
   - MinIO object storage
   - Redis message queue
   - Backend API (FastAPI)
   - Frontend (React)

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

5. **Default credentials**
   - Email: `admin@docflow.ai`
   - Password: `admin123`
   - **⚠️ Change these in production!**

6. **Ollama Setup (if using Ollama as LLM provider)**
   - Install Ollama on your host machine: https://ollama.ai
   - Pull a model: `ollama pull llama3.1` (or another model)
   - Ensure Ollama is running: `ollama serve`
   - **Memory Requirements**: Models need sufficient RAM:
     - `llama3.1` (8B): ~4.8 GiB
     - `mistral` (7B): ~4.1 GiB
     - If you get "model requires more system memory" errors:
       - Free up system memory
       - Use a smaller/quantized model
       - Increase Docker memory allocation (Settings → Resources → Memory)
   - Configure in `.env`:
     ```
     DEFAULT_LLM_PROVIDER=ollama
     OLLAMA_BASE_URL=http://localhost:11434
     OLLAMA_MODEL=llama3.1
     ```

### Local Development (without Docker)

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Database Setup**
   - Ensure PostgreSQL is running
   - Run migrations: `psql -U docflow -d docflow -f migrations/init.sql`

3. **Start Backend**
   ```bash
   uvicorn src.api.main:app --reload
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Project Structure

```
docflow-ai/
├── frontend/                    # React + TypeScript frontend
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   ├── pages/              # Page components
│   │   ├── contexts/           # React contexts (Auth)
│   │   └── services/           # API services
│   └── package.json
├── backend/                     # FastAPI backend (hexagonal architecture)
│   ├── src/
│   │   ├── domain/             # Domain layer (entities, services, events)
│   │   ├── application/        # Application layer (use cases, DTOs)
│   │   ├── infrastructure/      # Infrastructure layer (persistence, external services)
│   │   └── api/                 # API layer (routes, middleware)
│   ├── migrations/              # Database migrations
│   └── requirements.txt
├── docker-compose.yml           # Local development environment
└── README.md
```

## Architecture

The system follows **Hexagonal Architecture** (Ports & Adapters):

- **Domain Layer**: Core business logic, entities, value objects, domain services
- **Application Layer**: Use cases (orchestration), DTOs
- **Infrastructure Layer**: 
  - Persistence (PostgreSQL repositories)
  - External services (OCR, LLM, Storage)
  - Messaging (Redis queue)
- **API Layer**: FastAPI routes, middleware, authentication

## Key Features

- ✅ Document upload with validation
- ✅ OCR text extraction (PaddleOCR/Tesseract)
- ✅ LLM-based structured field extraction (OpenAI/Ollama)
- ✅ Document type classification (CMR, Invoice, Delivery Note)
- ✅ Validation engine with business rules
- ✅ Human-in-the-loop review and correction
- ✅ TMS export with retry logic
- ✅ Audit trail for all operations
- ✅ JWT authentication with RBAC
- ✅ Structured logging and metrics
- ✅ Error handling with retry strategies

## Troubleshooting

### Ollama Memory Issues

If you see errors like `"model requires more system memory (4.8 GiB) than is available (3.1 GiB)"`:

1. **Free up system memory**: Close other applications
2. **Use a smaller model**: Try a quantized version or smaller model
3. **Increase Docker memory**: Docker Desktop → Settings → Resources → Memory (increase to 6GB+)
4. **Check available models**: `ollama list` to see installed models and their sizes

### Extraction Returns Empty Structured Data

If OCR works but structured data extraction fails:

1. **Check extraction metadata** on the review page - it shows the exact error
2. **Verify Ollama connection**: `curl http://localhost:11434/api/tags`
3. **Check model availability**: Ensure the model specified in `OLLAMA_MODEL` is installed
4. **Review backend logs**: `docker-compose logs backend` for detailed error messages

### Frontend Can't Connect to Backend

1. **Check proxy configuration**: `frontend/package.json` should have `"proxy": "http://backend:8000"` for Docker
2. **Verify services are running**: `docker-compose ps`
3. **Check backend health**: `curl http://localhost:8000/health`

## License

MIT

