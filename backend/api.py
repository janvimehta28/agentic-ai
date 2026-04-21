"""Expose a minimal FastAPI stub endpoint for pipeline execution."""

from __future__ import annotations

from typing import Dict

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

HOST = "0.0.0.0"
PORT = 8000


class RunRequest(BaseModel):
    """Incoming request body for pipeline execution."""

    ticket: str


app = FastAPI(title="AutonomousDev API Stub")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/run")
def run_endpoint(request: RunRequest) -> Dict[str, str]:
    """Temporary endpoint stub; full pipeline wiring will be added later."""
    _ = request.ticket
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("api:app", host=HOST, port=PORT, reload=False)
