"""Serve AutonomousDev orchestration APIs and SSE status streams."""

from __future__ import annotations

import asyncio
import json
import os
import sys
import io
import uuid
from typing import Any, AsyncGenerator, Dict

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import uvicorn
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from pipeline.crew import run_pipeline
from report.aggregator import generate_report

CURRENT_DIRECTORY = os.path.dirname(__file__)
OUTPUT_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "output")
JOBS_STORE_FILE = os.path.join(OUTPUT_DIRECTORY, "jobs_store.json")
HOST = "0.0.0.0"
PORT = 8000
POLL_INTERVAL_SECONDS = 0.5


class RunRequest(BaseModel):
    """Incoming request body for pipeline execution."""

    ticket: str


class JobStatus:
    """Enumeration-like job state values for in-memory tracking."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


jobs: Dict[str, dict[str, Any]] = {}

app = FastAPI(title="AutonomousDev API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _save_jobs_to_disk() -> None:
    """Persist the in-memory jobs dictionary to disk."""
    try:
        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
        temp_file_path = f"{JOBS_STORE_FILE}.tmp"
        with open(temp_file_path, "w", encoding="utf-8") as file_handle:
            json.dump(jobs, file_handle, ensure_ascii=False, indent=2)
        os.replace(temp_file_path, JOBS_STORE_FILE)
    except Exception:
        # Keep API responsive even if persistence fails.
        return


def _load_jobs_from_disk() -> Dict[str, dict[str, Any]]:
    """Load persisted jobs from disk when available."""
    try:
        if not os.path.exists(JOBS_STORE_FILE):
            return {}
        with open(JOBS_STORE_FILE, "r", encoding="utf-8") as file_handle:
            loaded_jobs = json.load(file_handle)
        if isinstance(loaded_jobs, dict):
            return loaded_jobs
        return {}
    except Exception:
        return {}


def _append_job_log(job_id: str, message: str) -> None:
    """Append a log message to the tracked job when available."""
    job = jobs.get(job_id)
    if job is not None:
        job["logs"].append(message)
        _save_jobs_to_disk()


async def _run_pipeline_job(job_id: str, ticket: str) -> None:
    """Execute the pipeline in a worker thread and store outcomes in memory."""
    job = jobs.get(job_id)
    if job is None:
        return

    try:
        job["status"] = JobStatus.RUNNING
        _save_jobs_to_disk()

        def log_callback(message: str) -> None:
            """Capture asynchronous status updates for SSE clients."""
            _append_job_log(job_id, message)

        log_callback("Pipeline started.")
        event_loop = asyncio.get_event_loop()
        result = await event_loop.run_in_executor(None, run_pipeline, ticket)
        log_callback("Pipeline completed.")
        _ = generate_report(result)
        log_callback("Report generated at output/report.md.")

        job["result"] = result
        job["status"] = JobStatus.DONE
        _save_jobs_to_disk()
    except Exception as exc:  # pragma: no cover - runtime safety guard
        job["error"] = str(exc)
        job["status"] = JobStatus.ERROR
        _append_job_log(job_id, f"Pipeline failed: {exc}")
        _save_jobs_to_disk()


async def _event_stream(job_id: str) -> AsyncGenerator[str, None]:
    """Yield server-sent events for job logs and terminal status."""
    job = jobs.get(job_id)
    if job is None:
        payload = {"type": "error", "message": "Job not found"}
        yield f"data: {json.dumps(payload)}\n\n"
        return

    last_log_index = 0
    while True:
        try:
            current_job = jobs.get(job_id)
            if current_job is None:
                payload = {"type": "error", "message": "Job not found"}
                yield f"data: {json.dumps(payload)}\n\n"
                return

            new_logs = current_job["logs"][last_log_index:]
            for log_line in new_logs:
                payload = {"type": "log", "message": log_line}
                yield f"data: {json.dumps(payload)}\n\n"
            last_log_index += len(new_logs)

            if current_job["status"] == JobStatus.DONE:
                payload = {"type": "done", "result": current_job["result"]}
                yield f"data: {json.dumps(payload)}\n\n"
                return
            if current_job["status"] == JobStatus.ERROR:
                payload = {"type": "error", "message": current_job["error"]}
                yield f"data: {json.dumps(payload)}\n\n"
                return
        except Exception as exc:  # pragma: no cover - ensure stream resilience
            payload = {"type": "error", "message": f"Stream failure: {exc}"}
            yield f"data: {json.dumps(payload)}\n\n"
            return

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


@app.post("/run")
async def run_endpoint(request: RunRequest, background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Create a new job and dispatch pipeline execution in the background."""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": JobStatus.PENDING,
        "logs": [],
        "result": None,
        "error": None,
    }
    _save_jobs_to_disk()
    background_tasks.add_task(_run_pipeline_job, job_id, request.ticket)
    return {"job_id": job_id}


@app.get("/status/{job_id}")
async def status_endpoint(job_id: str) -> StreamingResponse:
    """Return a live SSE stream for the requested pipeline job."""
    return StreamingResponse(_event_stream(job_id), media_type="text/event-stream")


@app.get("/health")
async def health_endpoint() -> Dict[str, str]:
    """Return API liveness status."""
    return {"status": "ok"}


jobs = _load_jobs_from_disk()


if __name__ == "__main__":
    uvicorn.run("api:app", host=HOST, port=PORT, reload=False)
