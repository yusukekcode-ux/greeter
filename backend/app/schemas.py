from datetime import datetime
from pydantic import BaseModel
from app.models import VisitorStatus


class VisitorCreate(BaseModel):
    name: str
    purpose: str
    staff_name: str


class VisitorResponse(BaseModel):
    id: int
    ticket_number: int
    name: str
    purpose: str
    staff_name: str
    status: VisitorStatus
    created_at: datetime
    called_at: datetime | None
    done_at: datetime | None

    model_config = {"from_attributes": True}
