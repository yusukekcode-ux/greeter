from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Visitor, VisitorStatus
from app.state import broadcast


async def issue_ticket(
    db: AsyncSession, name: str, purpose: str, staff_name: str
) -> Visitor:
    result = await db.execute(
        select(func.max(Visitor.ticket_number)).where(
            func.date(Visitor.created_at) == func.date("now")
        )
    )
    max_num = result.scalar() or 0
    ticket_number = max_num + 1

    visitor = Visitor(
        ticket_number=ticket_number,
        name=name,
        purpose=purpose,
        staff_name=staff_name,
        status=VisitorStatus.waiting,
    )
    db.add(visitor)
    await db.commit()
    await db.refresh(visitor)

    await broadcast("new_visitor", {"ticket_number": ticket_number, "name": name})
    return visitor
