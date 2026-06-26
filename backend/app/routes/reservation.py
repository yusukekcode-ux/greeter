from datetime import date as date_type, time as time_type
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Reservation, ReservationStatus

router = APIRouter()
templates = Jinja2Templates(directory="templates")


async def _pending_reservations(db: AsyncSession):
    result = await db.execute(
        select(Reservation)
        .where(Reservation.status == ReservationStatus.pending)
        .order_by(Reservation.reserved_date, Reservation.reserved_time)
    )
    return result.scalars().all()


# --- 来訪者本人による事前予約 ---


@router.get("/reserve", response_class=HTMLResponse)
async def reserve_page(request: Request):
    return templates.TemplateResponse("reserve.html", {"request": request})


@router.post("/reserve", response_class=HTMLResponse)
async def create_reservation(
    request: Request,
    name: str = Form(...),
    purpose: str = Form(...),
    staff_name: str = Form(...),
    reserved_date: date_type = Form(...),
    reserved_time: time_type | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    reservation = Reservation(
        name=name,
        purpose=purpose,
        staff_name=staff_name,
        reserved_date=reserved_date,
        reserved_time=reserved_time,
        status=ReservationStatus.pending,
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)

    return templates.TemplateResponse(
        "partials/reservation_confirm.html",
        {"request": request, "reservation": reservation},
    )


# --- スタッフによる管理画面からの代理登録・一覧管理 ---


@router.get("/admin/reservations", response_class=HTMLResponse)
async def admin_reservations_page(request: Request, db: AsyncSession = Depends(get_db)):
    reservations = await _pending_reservations(db)
    return templates.TemplateResponse(
        "admin_reservations.html", {"request": request, "reservations": reservations}
    )


@router.post("/admin/reservations", response_class=HTMLResponse)
async def admin_create_reservation(
    request: Request,
    name: str = Form(...),
    purpose: str = Form(...),
    staff_name: str = Form(...),
    reserved_date: date_type = Form(...),
    reserved_time: time_type | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    reservation = Reservation(
        name=name,
        purpose=purpose,
        staff_name=staff_name,
        reserved_date=reserved_date,
        reserved_time=reserved_time,
        status=ReservationStatus.pending,
    )
    db.add(reservation)
    await db.commit()

    reservations = await _pending_reservations(db)
    return templates.TemplateResponse(
        "partials/admin_reservation_list.html",
        {"request": request, "reservations": reservations},
    )


@router.post("/admin/reservations/{reservation_id}/cancel", response_class=HTMLResponse)
async def admin_cancel_reservation(
    reservation_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    reservation = await db.get(Reservation, reservation_id)
    if reservation and reservation.status == ReservationStatus.pending:
        reservation.status = ReservationStatus.cancelled
        await db.commit()

    reservations = await _pending_reservations(db)
    return templates.TemplateResponse(
        "partials/admin_reservation_list.html",
        {"request": request, "reservations": reservations},
    )
