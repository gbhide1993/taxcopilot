from pydantic import BaseModel
from typing import List


class AppealResponse(BaseModel):
    notice_id: int
    version_number: int
    background: str
    grounds: str
    prayer: str

    class Config:
        from_attributes = True


class AppealVersionListResponse(BaseModel):
    notice_id: int
    versions: List[AppealResponse]
