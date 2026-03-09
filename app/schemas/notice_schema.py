from pydantic import BaseModel
from datetime import date
from typing import Optional, List
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

    act_name: Optional[str] = None
    section_reference: Optional[str] = None
    assessment_year: Optional[str] = None
    description: Optional[str] = None

    risk_score: Optional[float] = None

    received_date: date
    due_date: date

    status: str
    client_id: int
    client_name: Optional[str] = None

    assigned_to: Optional[int] = None

    # New Intelligence Fields
    risk_drivers: Optional[List[str]] = None
    recommended_action: Optional[str] = None
    risk_severity: Optional[str] = None

    assigned_user_name: Optional[str] = None

    class Config:
        from_attributes = True


class AssignmentResponse(BaseModel):
    message: str
    notice_id: int
    assigned_to: int