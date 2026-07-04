# Load environment variables
import config

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import (
    Base,
    engine
)

from api import (
    research_router,
    leads_router,
    review_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("Database connected successfully.")
    yield
    print("Application shutdown successfully.")


# Create FastAPI application
app = FastAPI(
    title="AI Business Research Analyst",
    description="""
    Multi-Agent AI system for B2B lead research.

    Features:
    - Google Sheet/Excel processing
    - LinkedIn lead discovery
    - Apollo enrichment
    - Company research
    - Revenue lookup
    - Email generation
    - Human review workflow
    """,
    version="1.0.0",
    lifespan=lifespan
)


# Allow all origins (safe for local dev; restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/")
def health_check():
    """
    API health check.
    """

    return {
        "application": "AI Business Research Analyst",
        "status": "RUNNING",
        "version": "1.0.0"
    }


# Register APIs
app.include_router(
    research_router
)

app.include_router(
    leads_router
)

app.include_router(
    review_router
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)