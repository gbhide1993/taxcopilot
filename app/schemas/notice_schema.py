from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.models.notice import NoticeStatus


class NoticeCreate(BaseModel):
    notice_number: str
    notice_type: str
    act_name: str
    section_reference: str
    assessment_year: Optional[str] = None
    description: Optional[str] = None
    received_date: date
    due_date: date
    client_id: int


class NoticeUpdateStatus(BaseModel):
    status: NoticeStatus


class NoticeAssign(BaseModel):
    assigned_to: int


class NoticeResponse(BaseModel):
    id: int
    notice_number: str
    notice_type: str
    act_name: str
    section_reference: str | None
    assessment_year: str | None
    description: str | None
    received_date: date
    due_date: date
    status: str
    client_id: int
    assigned_to: int | None

    class Config:
        from_attributes = True
