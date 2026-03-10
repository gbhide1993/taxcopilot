from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.section_service import get_section_by_act_and_number
from app.schemas.section_schema import SectionResponse

router = APIRouter(
    prefix="/sections",
    tags=["Sections"]
)


@router.get("/{act_name}/{section_reference}", response_model=SectionResponse)
def get_section(
    act_name: str,
    section_reference: str,
    db: Session = Depends(get_db)
):
    return get_section_by_act_and_number(
        db,
        act_name,
        section_reference
    )
