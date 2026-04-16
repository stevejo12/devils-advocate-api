"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import debate

app = FastAPI(
  title="Devil's Advocate",
  description="AI-powered thinking companion with three debate personas.",
  version="0.1.0",
)

# CORS — allow the frontend origin from settings
app.add_middleware(
  CORSMiddleware,
  allow_origins=[settings.frontend_origin],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Register routers
app.include_router(debate.router)

@app.get("/health")
async def health_check() -> dict[str, str]:
  return {"status": "ok"}
