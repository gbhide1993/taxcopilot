from pydantic import BaseModel
from typing import List


class DraftResponse(BaseModel):
    notice_id: int
    version_number: int
    introduction: str
    facts_summary: str
    legal_position: str
    section_reference: str
    prayer: str

    class Config:
        from_attributes = True

class DraftVersionListResponse(BaseModel):
    notice_id: int
    versions: List[DraftResponse]