"""
FinSight AI — FastAPI Application
Main entry point for the backend server.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ml.inference import engine
from app.database import init_db
from app.api.analyze import router as analyze_router
from app.api.batch import router as batch_router
from app.api.compare import router as compare_router
from app.api.analytics import router as analytics_router
from app.api.model import router as model_router
from app.api.history import router as history_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # ─── Startup ──────────────────────────────────────────
    print("=" * 50)
    print("  FinSight AI — Starting Up")
    print("=" * 50)

    # Initialize database
    await init_db()

    # Load model
    loaded = engine.load()
    if loaded:
        print("[+] Model loaded successfully")
    else:
        print("[!] Model not available — run training first")

    print("[+] Server ready")
    print("=" * 50)

    yield

    # ─── Shutdown ─────────────────────────────────────────
    print("[*] Shutting down FinSight AI")


app = FastAPI(
    title="FinSight AI",
    description="Custom Transformer-based Financial Sentiment Analysis Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(analyze_router)
app.include_router(batch_router)
app.include_router(compare_router)
app.include_router(analytics_router)
app.include_router(model_router)
app.include_router(history_router)


@app.get("/")
async def root():
    return {
        "name": "FinSight AI",
        "version": "1.0.0",
        "status": "online" if engine.is_loaded else "model_not_loaded",
        "description": "Custom Transformer-based Financial Sentiment Analysis",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": engine.is_loaded,
        "model_info": engine.get_model_info() if engine.is_loaded else None,
    }
