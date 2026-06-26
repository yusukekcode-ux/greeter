from datetime import datetime, date, time
from sqlalchemy import Integer, String, DateTime, Date, Time, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class VisitorStatus(str, enum.Enum):
    waiting = "waiting"
    called = "called"
    done = "done"
    cancelled = "cancelled"


class Visitor(Base):
    __tablename__ = "visitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_number: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    purpose: Mapped[str] = mapped_column(String(200), nullable=False)
    staff_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[VisitorStatus] = mapped_column(
        Enum(VisitorStatus), default=VisitorStatus.waiting, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    called_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    done_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ReservationStatus(str, enum.Enum):
    pending = "pending"
    checked_in = "checked_in"
    cancelled = "cancelled"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    purpose: Mapped[str] = mapped_column(String(200), nullable=False)
    staff_name: Mapped[str] = mapped_column(String(100), nullable=False)
    reserved_date: Mapped[date] = mapped_column(Date, nullable=False)
    reserved_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus), default=ReservationStatus.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    visitor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("visitors.id"), nullable=True
    )
