# backend/models.py
from typing import Optional
from pydantic import BaseModel


class TaskRequest(BaseModel):
    input: str  # user message, e.g. "Weather in SLC?"


class TaskStatus(BaseModel):
    task_id: str
    status: str               # "queued" | "running" | "done" | "error"
    result: Optional[str] = None
    error: Optional[str] = None


class TaskEvent(BaseModel):
    """
    An event that the backend can send to the frontend via /events.
    For this demo, events are emitted when a task finishes (done/error).
    """
    event_id: int
    task_id: str
    status: str               # "done" | "error"
    result: Optional[str] = None
    error: Optional[str] = None
