# backend/task_queue.py
import asyncio
from typing import Dict, List

from .models import TaskStatus, TaskEvent

# Async task queue (purple box in the diagram)
task_queue: asyncio.Queue = asyncio.Queue()

# In-memory task store by id
tasks: Dict[str, TaskStatus] = {}

# In-memory event stream (for /events)
events: List[TaskEvent] = []
_next_event_id: int = 1


def add_event(task_id: str, status: str, result: str | None, error: str | None):
    """
    Append a new event to the in-memory event list.
    """
    global _next_event_id
    ev = TaskEvent(
        event_id=_next_event_id,
        task_id=task_id,
        status=status,
        result=result,
        error=error,
    )
    events.append(ev)
    _next_event_id += 1
