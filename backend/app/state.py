import asyncio
from typing import Any

# SSE subscribers: list of asyncio.Queue
_subscribers: list[asyncio.Queue] = []


def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _subscribers.append(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    try:
        _subscribers.remove(q)
    except ValueError:
        pass


async def broadcast(event: str, data: Any) -> None:
    dead = []
    for q in _subscribers:
        try:
            q.put_nowait({"event": event, "data": data})
        except asyncio.QueueFull:
            dead.append(q)
    for q in dead:
        unsubscribe(q)
