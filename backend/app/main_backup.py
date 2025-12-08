from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from contextlib import asynccontextmanager

from app.api.endpoints import pnodes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("?? Starting Xandeum pNode Dashboard API...")
    yield
    # Shutdown
    print("?? Shutting down...")

app = FastAPI(
    title="Xandeum pNode Dashboard",
    description="Analytics platform for Xandeum proof nodes",
    version="1.0.0",
    lifespan=lifespan
)
app.include_router(
   pnodes.router)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "Xandeum pNode Dashboard API",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "pnodes": "/api/pnodes"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}

@app.get("/api/pnodes")
async def get_pnodes():
    # TODO: Connect to Xandeum pRPC
    return {"message": "pNodes endpoint - implement Xandeum pRPC connection"}
