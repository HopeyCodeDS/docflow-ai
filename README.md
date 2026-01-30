# DocFlow AI - Intelligent Transport Document Processing Platform

A full-stack system for ingesting logistics documents (PDF/images), extracting structured data, validating it, enabling human correction, and integrating results into downstream workflows.

## Architecture

The system follows **Hexagonal Architecture** (Ports & Adapters):

- **Domain Layer**: Core business logic, entities, value objects, domain services
- **Application Layer**: Use cases (orchestration), DTOs
- **Infrastructure Layer**:
  - Persistence (PostgreSQL repositories)
  - External services (OCR, LLM, Storage)
  - Messaging (Redis queue)
- **API Layer**: FastAPI routes, middleware, authentication

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

- Document upload (PDF, images) with validation
- OCR text extraction (PaddleOCR/Tesseract) and layout-aware extraction
- LLM-based structured field extraction (OpenAI/Ollama)
- Document type classification (CMR, Invoice, Delivery Note)
- Validation engine with business rules and confidence scoring
- Human-in-the-loop review and correction UI
- TMS export with retry logic
- Audit trail and versioning for all operations
- JWT authentication with RBAC
- Structured logging, metrics, error handling with retries

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/HopeyCodeDS/docflow-ai
   cd DocFlow-AI
   ```

2. **Configure environment variables**
   - Copy `.env.example` to `.env` (if it exists) or set environment variables for database, storage, and API keys.

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```
   This starts: PostgreSQL, MinIO, Redis, Backend (FastAPI), Frontend (React).

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - MinIO Console: http://localhost:9001 (default: minioadmin/minioadmin)

5. **Optional: Ollama (local LLM)**  
   Install [Ollama](https://ollama.ai), run `ollama pull llama3.1`, then set in `.env`:
   ```
   DEFAULT_LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.1
   ```

### Local Development (without Docker)

1. **Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
   Ensure PostgreSQL is running and run migrations: `psql -U docflow -d docflow -f migrations/init.sql`
   ```bash
   uvicorn src.api.main:app --reload
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Running tests

- **Backend**: `cd backend && pytest`
- **Frontend**: `cd frontend && npm test`

## Project Structure

```
DocFlow-AI/
├── frontend/                    # React + TypeScript
│   ├── src/
│   │   ├── components/          # Reusable components
│   │   ├── pages/               # Page components
│   │   ├── contexts/            # React contexts (Auth)
│   │   └── services/            # API services
│   └── package.json
├── backend/                     # FastAPI (hexagonal architecture)
│   ├── src/
│   │   ├── domain/              # Domain layer (entities, services, events)
│   │   ├── application/         # Application layer (use cases, DTOs)
│   │   ├── infrastructure/      # Infrastructure (persistence, OCR, LLM, storage, messaging)
│   │   └── api/                 # API layer (routes, middleware)
│   ├── migrations/
│   └── requirements.txt
├── scripts/                     # Utility scripts (see scripts/README.md)
├── docker-compose.yml
└── README.md
```

## License

MIT
