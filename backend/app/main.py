from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes import kiosk, admin, display, reservation


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Greeter", lifespan=lifespan)

app.include_router(kiosk.router)
app.include_router(admin.router)
app.include_router(display.router)
app.include_router(reservation.router)


@app.get("/")
async def root():
    return {"status": "ok"}
