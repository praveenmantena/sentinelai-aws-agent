from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class StrandsTask:
    name: str
    run: Callable[..., Any]


class StrandsWorkflow:
    def __init__(self) -> None:
        self._tasks: list[StrandsTask] = []

    def add_task(self, name: str, run: Callable[..., Any]) -> None:
        self._tasks.append(StrandsTask(name=name, run=run))

    def execute(self, **context: Any) -> dict[str, Any]:
        state = dict(context)
        for task in self._tasks:
            state[task.name] = task.run(state)
        return state


try:
    from strands import Agent as _StrandsAgent  # type: ignore
except Exception:
    _StrandsAgent = None


class BaseStrandsCompatibleAgent:
    def __init__(self, name: str) -> None:
        self.name = name
        self.native_agent = _StrandsAgent(name=name) if _StrandsAgent else None
