# SEC Edgar Regulatory Document Explorer

An AI-enhanced regulatory document discovery application that fetches SEC filings, stores them with a RAG-ready architecture, and provides an intuitive interface for browsing and searching regulatory documents.

## Architecture

```
┌─────────────────┐
│  React Frontend │
│  (Vite + Tailwind)
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend│
└────┬───────┬────┘
     │       │
     │       └─────────────┐
     ▼                     ▼
┌──────────┐        ┌─────────────┐
│ Supabase │        │  Weaviate   │
│(Metadata)│        │  (Chunks)   │
└──────────┘        └─────────────┘
     ▲                     ▲
     │                     │
     └──────────┬──────────┘
                │
         ┌──────▼──────┐
         │  SEC Edgar  │
         │     API     │
         └─────────────┘
```

## Features

- **Fetch Regulatory Data**: Integrated with SEC Edgar API for real-time filings.
- **Document List Display**: Responsive grid layout with color-coded badges and status indicators.
- **Detail View**: Comprehensive modal with metadata, content preview, and links to official SEC documents.
- **RAG-Ready Architecture**: Document chunking and vector storage (Weaviate) for future AI-powered semantic search.
- **Responsive Design**: Optimized for mobile, tablet, and desktop using Tailwind CSS.

## Quick Start

### 1. Setup Environment
Update the `.env` files based on the `.env.example` in both frontend and backend directories:
- `backend/.env`
- `frontend/.env`

### 2. Run for Development

#### Backend
```bash
cd backend
uv sync

# Activate it (Windows)
.venv\Scripts\activate

# Activate it (macOS/Linux)
source .venv/bin/activate

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend will be available at **http://localhost:8000**

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at **http://localhost:5173**

### 3. Run with Docker
To run the entire stack using Docker:
```bash
docker compose up
```

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Weaviate (Vector DB), Supabase (PostgreSQL)
- **Frontend**: React, Vite, Tailwind CSS
- **Tools**: `uv` for Python package management, `npm` for frontend
