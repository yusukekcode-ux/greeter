from datetime import datetime
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Visitor, VisitorStatus
from app.state import broadcast

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Visitor)
        .where(Visitor.status.in_([VisitorStatus.waiting, VisitorStatus.called]))
        .order_by(Visitor.ticket_number)
    )
    visitors = result.scalars().all()
    return templates.TemplateResponse(
        "admin.html", {"request": request, "visitors": visitors}
    )


@router.get("/admin/visitors", response_class=HTMLResponse)
async def visitors_list(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Visitor)
        .where(Visitor.status.in_([VisitorStatus.waiting, VisitorStatus.called]))
        .order_by(Visitor.ticket_number)
    )
    visitors = result.scalars().all()
    return templates.TemplateResponse(
        "partials/visitors_list.html", {"request": request, "visitors": visitors}
    )


@router.post("/admin/call/{visitor_id}", response_class=HTMLResponse)
async def call_visitor(
    visitor_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    visitor = await db.get(Visitor, visitor_id)
    if visitor and visitor.status == VisitorStatus.waiting:
        visitor.status = VisitorStatus.called
        visitor.called_at = datetime.now()
        await db.commit()
        await db.refresh(visitor)
        await broadcast(
            "called",
            {
                "ticket_number": visitor.ticket_number,
                "name": visitor.name,
                "staff_name": visitor.staff_name,
            },
        )

    result = await db.execute(
        select(Visitor)
        .where(Visitor.status.in_([VisitorStatus.waiting, VisitorStatus.called]))
        .order_by(Visitor.ticket_number)
    )
    visitors = result.scalars().all()
    return templates.TemplateResponse(
        "partials/visitors_list.html", {"request": request, "visitors": visitors}
    )


@router.post("/admin/done/{visitor_id}", response_class=HTMLResponse)
async def done_visitor(
    visitor_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    visitor = await db.get(Visitor, visitor_id)
    if visitor and visitor.status == VisitorStatus.called:
        visitor.status = VisitorStatus.done
        visitor.done_at = datetime.now()
        await db.commit()
        await broadcast("done", {"ticket_number": visitor.ticket_number})

    result = await db.execute(
        select(Visitor)
        .where(Visitor.status.in_([VisitorStatus.waiting, VisitorStatus.called]))
        .order_by(Visitor.ticket_number)
    )
    visitors = result.scalars().all()
    return templates.TemplateResponse(
        "partials/visitors_list.html", {"request": request, "visitors": visitors}
    )


@router.post("/admin/cancel/{visitor_id}", response_class=HTMLResponse)
async def cancel_visitor(
    visitor_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    visitor = await db.get(Visitor, visitor_id)
    if visitor and visitor.status in [VisitorStatus.waiting, VisitorStatus.called]:
        visitor.status = VisitorStatus.cancelled
        await db.commit()
        await broadcast("cancelled", {"ticket_number": visitor.ticket_number})

    result = await db.execute(
        select(Visitor)
        .where(Visitor.status.in_([VisitorStatus.waiting, VisitorStatus.called]))
        .order_by(Visitor.ticket_number)
    )
    visitors = result.scalars().all()
    return templates.TemplateResponse(
        "partials/visitors_list.html", {"request": request, "visitors": visitors}
    )
