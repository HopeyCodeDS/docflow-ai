# Sortex.AI

Intelligent document processing platform for transport and logistics. Upload PDF or image documents, automatically classify them, extract structured data with OCR + LLM, validate against business rules, and review results in a human-in-the-loop UI.

## Features

- **Document classification** — automatically identifies 11 transport document types (CMR, Invoice, Bill of Lading, Air Waybill, Customs Declaration, and more) using weighted keyword scoring with fuzzy matching and LLM fallback
- **OCR extraction** — PaddleOCR (default) or Tesseract for text extraction from PDFs and images
- **LLM field extraction** — structured field extraction via Ollama (qwen2.5:3b) or OpenAI, with per-document-type schemas
- **Validation engine** — config-driven business rules with confidence scoring
- **Review UI** — human-in-the-loop correction interface with side-by-side document viewer
- **Authentication** — JWT access/refresh tokens with role-based access control (RBAC)
- **File security** — magic bytes validation, filename sanitization, rate limiting

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Tailwind CSS, Lucide icons |
| Backend | Python 3.11, FastAPI, SQLAlchemy, Pydantic v2 |
| OCR | PaddleOCR / Tesseract (pluggable) |
| LLM | Ollama (qwen2.5:3b) / OpenAI (pluggable) |
| Database | PostgreSQL 15 |
| Storage | MinIO (S3-compatible) |
| Queue | Redis 7 |
| Monitoring | OpenTelemetry, Prometheus |

## Architecture

Hexagonal Architecture (Ports & Adapters):

```
backend/src/
├── domain/           # Entities, value objects, domain services
├── application/      # Use cases, DTOs, extraction schemas
├── infrastructure/   # Repositories, OCR, LLM, storage, auth, messaging
└── api/              # FastAPI routes, middleware
```

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Ollama](https://ollama.ai) installed locally (for LLM extraction)

### 1. Clone and configure

```bash
git clone https://github.com/HopeyCodeDS/sortex-ai.git
cd sortex-ai
```

Create a `.env` file in the project root:

```env
POSTGRES_USER=sortex
POSTGRES_PASSWORD=sortex
POSTGRES_DB=sortex

MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

JWT_SECRET_KEY=change-this-in-production

DEFAULT_LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b

CORS_ORIGINS=http://localhost:3000
```

### 2. Pull the Ollama model

```bash
ollama pull qwen2.5:3b
```

### 3. Start services

```bash
docker-compose up -d
```

This starts PostgreSQL, MinIO, Redis, the FastAPI backend, and the React frontend.

### 4. Access the app

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| MinIO console | http://localhost:9001 |

Default login: `admin@docflow.ai` / `admin123`

## Project Structure

```
sortex-ai/
├── frontend/                     # React + TypeScript + Tailwind
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/           # AppLayout, Sidebar, TopBar
│   │   │   └── ui/               # Reusable components (Card, Modal, DataTable, etc.)
│   │   ├── pages/                # Dashboard, DocumentUpload, DocumentReview, Login
│   │   ├── contexts/             # Auth context
│   │   └── services/             # API client
│   └── package.json
├── backend/                      # FastAPI + Hexagonal Architecture
│   ├── src/
│   │   ├── domain/
│   │   │   ├── entities/         # Document, Extraction, User
│   │   │   └── services/         # Classification, validation
│   │   ├── application/
│   │   │   ├── use_cases/        # Extract fields, process document
│   │   │   └── extraction_schemas.py
│   │   ├── infrastructure/
│   │   │   ├── persistence/      # PostgreSQL repositories
│   │   │   ├── ocr/              # PaddleOCR, Tesseract adapters
│   │   │   ├── llm/              # Ollama, OpenAI adapters
│   │   │   ├── storage/          # MinIO adapter
│   │   │   └── auth/             # JWT, RBAC
│   │   └── api/
│   │       └── routes/           # REST endpoints
│   ├── migrations/
│   └── requirements.txt
├── docker-compose.yml
└── .env
```

## Supported Document Types

| Type | Description |
|------|-------------|
| CMR | Convention Marchandise Routiers (road consignment) |
| Invoice | Commercial / freight invoices |
| Delivery Note | Proof of delivery documents |
| Bill of Lading | Ocean shipping contracts |
| Air Waybill | Air cargo consignment notes |
| Sea Waybill | Non-negotiable sea transport |
| Packing List | Shipment contents listing |
| Customs Declaration | Import/export customs forms |
| Certificate of Origin | Country of origin certification |
| Dangerous Goods Declaration | Hazmat shipping declarations |
| Freight Bill | Carrier billing documents |

## Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

Requires PostgreSQL, Redis, and MinIO running locally or via Docker.

## License

MIT
