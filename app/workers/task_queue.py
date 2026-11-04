"""Typed data classes for communication between main thread and DB worker."""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class DBTask:
    action: str
    payload: Dict[str, Any] = field(default_factory=dict)
    task_id: int = 0
    callback: str = ""


@dataclass
class Result:
    task_id: int
    data: Any = None
    error: str = ""
    callback: str = ""
