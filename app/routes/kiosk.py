from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Reservation, ReservationStatus
from app.ticketing import issue_ticket

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/kiosk", response_class=HTMLResponse)
async def kiosk_page(request: Request):
    return templates.TemplateResponse("kiosk.html", {"request": request})


@router.post("/kiosk/register", response_class=HTMLResponse)
async def register(
    request: Request,
    name: str = Form(...),
    purpose: str = Form(...),
    staff_name: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    visitor = await issue_ticket(db, name, purpose, staff_name)
    return templates.TemplateResponse(
        "partials/ticket.html",
        {"request": request, "visitor": visitor},
    )


@router.get("/kiosk/reservations", response_class=HTMLResponse)
async def pending_reservations(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Reservation)
        .where(Reservation.status == ReservationStatus.pending)
        .order_by(Reservation.reserved_date, Reservation.reserved_time)
    )
    reservations = result.scalars().all()
    return templates.TemplateResponse(
        "partials/kiosk_reservations.html",
        {"request": request, "reservations": reservations},
    )


@router.post("/kiosk/reservations/{reservation_id}/checkin", response_class=HTMLResponse)
async def checkin_reservation(
    reservation_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    reservation = await db.get(Reservation, reservation_id)
    if not reservation or reservation.status != ReservationStatus.pending:
        return templates.TemplateResponse(
            "partials/kiosk_error.html",
            {"request": request, "message": "この予約は受付できません。"},
        )

    visitor = await issue_ticket(
        db, reservation.name, reservation.purpose, reservation.staff_name
    )
    reservation.status = ReservationStatus.checked_in
    reservation.visitor_id = visitor.id
    await db.commit()

    return templates.TemplateResponse(
        "partials/ticket.html", {"request": request, "visitor": visitor}
    )
