from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import palette
from app.config import settings

app = FastAPI(
    title="Color Whisperer API",
    description="Send any color, get back your season, vibe, and a curated palette.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(palette.router, prefix="/v1")


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Color Whisperer API is alive. Send us a color."}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
