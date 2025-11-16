# backend/api.py
import asyncio
import os
import uuid
from typing import List

from fastapi import FastAPI, HTTPException

from .models import TaskRequest, TaskStatus, TaskEvent
from .task_queue import task_queue, tasks, events
from .worker import worker_loop

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY not set")

app = FastAPI(
    title="Weather Agent Backend",
    description="Backend with background task queue running the Smart Weather Agent",
)


@app.on_event("startup")
async def startup_event():
    # Start background worker when app starts
    asyncio.create_task(worker_loop())


@app.post("/tasks", response_model=TaskStatus)
async def create_task(req: TaskRequest):
    """
    Frontend sends a user query here.
    We enqueue the task and return a task_id immediately.
    """
    task_id = str(uuid.uuid4())
    task_status = TaskStatus(task_id=task_id, status="queued")
    tasks[task_id] = task_status

    await task_queue.put((task_id, req.input))
    return task_status


@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """
    Optional: direct task status lookup.
    (Not strictly needed if you only use /events, but handy for debugging.)
    """
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/events", response_model=List[TaskEvent])
async def get_events():
    """
    Frontend calls /events to receive any completed task events.
    For demo simplicity, we return all current events and then clear the list.
    """
    current_events = list(events)
    events.clear()
    return current_events
