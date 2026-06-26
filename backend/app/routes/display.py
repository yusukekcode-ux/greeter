import asyncio
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.state import subscribe, unsubscribe

router = APIRouter()


@router.get("/api/sse")
async def sse(request: Request):
    queue = subscribe()

    async def event_generator():
        try:
            yield "data: {\"event\": \"connected\"}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    payload = json.dumps({"event": msg["event"], "data": msg["data"]})
                    yield f"data: {payload}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
