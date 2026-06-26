from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from app.database import init_db
from app.routes import kiosk, admin, display, reservation


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Greeter", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(kiosk.router)
app.include_router(admin.router)
app.include_router(display.router)
app.include_router(reservation.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/kiosk")
