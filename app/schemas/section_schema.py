from pydantic import BaseModel
from typing import Optional, Dict, Any


class SectionResponse(BaseModel):
    act_name: str
    section_number: str
    heading: str
    full_text: str
    severity_level: int
    penalty_flag: bool
    annexure_template: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True
