"""
Main FastAPI application.
Entry point for the SEC Edgar regulatory document explorer API.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from .database import init_db, get_db
from .routers import documents, search
from .services.weaviate_service import WeaviateService
from .services.gemini_service import GeminiService
from .services.sec_service import SECService
from .services.chunking_service import ChunkingService
from .services.document_service import DocumentService
from .services.search_service import SearchService

# Initialize service instances at app startup
weaviate_service = WeaviateService()
gemini_service = GeminiService()
sec_service = SECService()
chunking_service = ChunkingService()
document_service = DocumentService()
search_service = SearchService(weaviate_service)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up...")
    
    # Initialize database
    init_db()
    
    # Initialize filing types
    db = next(get_db())
    try:
        document_service.initialize_filing_types(db)
        logger.info("Filing types initialized")
    except Exception as e:
        logger.error(f"Error initializing filing types: {e}")
    finally:
        db.close()
    
    # Initialize Weaviate schema
    try:
        if weaviate_service.is_connected():
            weaviate_service.create_schema()
            logger.info("Weaviate schema initialized")
        else:
            logger.warning("Warning: Weaviate is not connected")
    except Exception as e:
        logger.error(f"Error initializing Weaviate: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    weaviate_service.close()


# Create FastAPI application
app = FastAPI(
    title="SEC Edgar Regulatory Document Explorer",
    description="API for exploring SEC regulatory filings with RAG-ready architecture",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite and CRA defaults
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router)
app.include_router(search.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "SEC Edgar Regulatory Document Explorer API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

