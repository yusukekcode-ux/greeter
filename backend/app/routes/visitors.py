from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Visitor, VisitorStatus
from app.schemas import VisitorCreate, VisitorResponse
from app.state import broadcast
from app.ticketing import issue_ticket

router = APIRouter(prefix="/api/visitors", tags=["visitors"])


@router.get("", response_model=list[VisitorResponse])
async def list_visitors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Visitor)
        .where(Visitor.status.in_([VisitorStatus.waiting, VisitorStatus.called]))
        .order_by(Visitor.ticket_number)
    )
    return result.scalars().all()


@router.post("", response_model=VisitorResponse, status_code=201)
async def create_visitor(body: VisitorCreate, db: AsyncSession = Depends(get_db)):
    return await issue_ticket(db, body.name, body.purpose, body.staff_name)


@router.post("/{visitor_id}/call", response_model=VisitorResponse)
async def call_visitor(visitor_id: int, db: AsyncSession = Depends(get_db)):
    visitor = await db.get(Visitor, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    if visitor.status != VisitorStatus.waiting:
        raise HTTPException(status_code=409, detail="Visitor is not waiting")

    visitor.status = VisitorStatus.called
    visitor.called_at = datetime.now()
    await db.commit()
    await db.refresh(visitor)
    await broadcast("called", {
        "ticket_number": visitor.ticket_number,
        "name": visitor.name,
        "staff_name": visitor.staff_name,
    })
    return visitor


@router.post("/{visitor_id}/done", response_model=VisitorResponse)
async def done_visitor(visitor_id: int, db: AsyncSession = Depends(get_db)):
    visitor = await db.get(Visitor, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    if visitor.status != VisitorStatus.called:
        raise HTTPException(status_code=409, detail="Visitor is not called")

    visitor.status = VisitorStatus.done
    visitor.done_at = datetime.now()
    await db.commit()
    await db.refresh(visitor)
    await broadcast("done", {"ticket_number": visitor.ticket_number})
    return visitor


@router.post("/{visitor_id}/cancel", response_model=VisitorResponse)
async def cancel_visitor(visitor_id: int, db: AsyncSession = Depends(get_db)):
    visitor = await db.get(Visitor, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    if visitor.status not in [VisitorStatus.waiting, VisitorStatus.called]:
        raise HTTPException(status_code=409, detail="Visitor cannot be cancelled")

    visitor.status = VisitorStatus.cancelled
    await db.commit()
    await db.refresh(visitor)
    await broadcast("cancelled", {"ticket_number": visitor.ticket_number})
    return visitor
