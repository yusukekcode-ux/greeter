from datetime import datetime, date, time
from pydantic import BaseModel
from app.models import VisitorStatus, ReservationStatus


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


class ReservationCreate(BaseModel):
    name: str
    purpose: str
    staff_name: str
    reserved_date: date
    reserved_time: time | None = None


class ReservationResponse(BaseModel):
    id: int
    name: str
    purpose: str
    staff_name: str
    reserved_date: date
    reserved_time: time | None
    status: ReservationStatus
    created_at: datetime
    visitor_id: int | None

    model_config = {"from_attributes": True}
