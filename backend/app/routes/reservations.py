from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Reservation, ReservationStatus
from app.schemas import ReservationCreate, ReservationResponse, VisitorResponse
from app.ticketing import issue_ticket

router = APIRouter(prefix="/api/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationResponse])
async def list_reservations(
    status: ReservationStatus | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Reservation).order_by(Reservation.reserved_date, Reservation.reserved_time)
    if status:
        query = query.where(Reservation.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ReservationResponse, status_code=201)
async def create_reservation(body: ReservationCreate, db: AsyncSession = Depends(get_db)):
    reservation = Reservation(
        name=body.name,
        purpose=body.purpose,
        staff_name=body.staff_name,
        reserved_date=body.reserved_date,
        reserved_time=body.reserved_time,
        status=ReservationStatus.pending,
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)
    return reservation


@router.post("/{reservation_id}/checkin", response_model=VisitorResponse)
async def checkin_reservation(reservation_id: int, db: AsyncSession = Depends(get_db)):
    reservation = await db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(status_code=409, detail="Reservation is not pending")

    visitor = await issue_ticket(db, reservation.name, reservation.purpose, reservation.staff_name)
    reservation.status = ReservationStatus.checked_in
    reservation.visitor_id = visitor.id
    await db.commit()
    return visitor


@router.post("/{reservation_id}/cancel", response_model=ReservationResponse)
async def cancel_reservation(reservation_id: int, db: AsyncSession = Depends(get_db)):
    reservation = await db.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(status_code=409, detail="Reservation is not pending")

    reservation.status = ReservationStatus.cancelled
    await db.commit()
    await db.refresh(reservation)
    return reservation
