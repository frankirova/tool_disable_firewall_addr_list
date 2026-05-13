"""Application entry point — composition root.

Only this file knows how everything is assembled.
Run with: uvicorn refactor.main:api --reload
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from refactor.api.router import router
from refactor.core.config import config

HERE = Path(__file__).parent

api = FastAPI(title="IP Suspension Tool")

api.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
api.include_router(router)


@api.get("/")
async def root() -> FileResponse:
    return FileResponse(HERE / "static" / "index.html")
