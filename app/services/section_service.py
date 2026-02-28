from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.sections_master import SectionsMaster


def get_section_by_act_and_number(
    db: Session,
    act_name: str,
    section_reference: str
) -> SectionsMaster:

    stmt = select(SectionsMaster).where(
        SectionsMaster.act_name == act_name,
        SectionsMaster.section_reference == section_reference
    )

    section = db.execute(stmt).scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found. Exact match required."
        )

    return section
