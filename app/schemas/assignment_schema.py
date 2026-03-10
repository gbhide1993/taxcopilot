from pydantic import BaseModel


class AssignNoticeRequest(BaseModel):
    assigned_to: int
    role: str


class AssignNoticeResponse(BaseModel):
    notice_id: int
    assigned_to: int
    message: str
