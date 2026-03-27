from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import os
from .database import engine, Base, init_db
from . import models
from core.config import settings

# Import all routers
from .routers import auth, chat, products, orders, voice
from .routers import market, matching, suppliers, trust, community
from .routers import payments, analytics, notifications, reports, websocket, sync
from .routers import recommendations, posts

# Create all database tables
init_db()

app = FastAPI(
    title="Ooumph Agentic AI Ecosystem API",
    description="API for SHG Smart Market Linkage Platform",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware - TrustedHost (only in production)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["ooumph.com", "*.ooumph.com", "localhost"]
    )

# CORS middleware - allow all localhost origins in development
import re

def is_allowed_origin(origin: str) -> bool:
    return bool(re.match(r'http://localhost:\d+', origin))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [settings.FRONTEND_URL, "http://localhost:6001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip middleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files for uploads
uploads_dir = os.getenv("UPLOADS_DIR", "/app/uploads")
try:
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(f"{uploads_dir}/audio", exist_ok=True)
    os.makedirs(f"{uploads_dir}/images", exist_ok=True)
except PermissionError:
    # Use temp directory if no permission
    import tempfile
    uploads_dir = os.path.join(tempfile.gettempdir(), "ooumph_uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(f"{uploads_dir}/audio", exist_ok=True)
    os.makedirs(f"{uploads_dir}/images", exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include all routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat/Vaani"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(market.router, prefix="/api/market", tags=["Market Intelligence"])
app.include_router(matching.router, prefix="/api/matching", tags=["Buyer Matching"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["Suppliers/Materials"])
app.include_router(trust.router, prefix="/api/trust", tags=["Trust & Compliance"])
app.include_router(community.router, prefix="/api/community", tags=["Community"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(websocket.router, prefix="/api", tags=["WebSocket"])
app.include_router(sync.router, prefix="/api/sync", tags=["Offline Sync"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])
app.include_router(posts.router, prefix="/api", tags=["Posts"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Ooumph Agentic AI Ecosystem API",
        "version": "1.0.0",
        "docs": "/docs",
        "agents": ["Vaani", "Bazaar Buddhi", "Jodi", "Samagri", "Vishwas", "Sampark"]
    }

@app.get("/health")
def health_check():
    """Health check endpoint with system information"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "features": {
            "websocket": settings.ENABLE_WEBSOCKET,
            "cache": settings.ENABLE_CACHE,
            "rate_limiting": settings.RATE_LIMIT_ENABLED
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    # Initialize logging
    from core.logging import setup_logging
    setup_logging()

    # Initialize database
    init_db()

    # Log startup
    from core.logging import get_logger
    logger = get_logger(__name__)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}",
                extra={"environment": settings.ENVIRONMENT})
