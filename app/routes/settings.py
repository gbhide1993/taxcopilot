from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.firm_settings import FirmSettings
from pydantic import BaseModel

router = APIRouter(prefix="/settings", tags=["Settings"])


class FirmSettingsResponse(BaseModel):

    auto_generate_draft: bool
    auto_generate_risk: bool

    draft_sla_days: int
    review_sla_days: int
    submission_sla_days: int

    class Config:
        from_attributes = True


@router.get("/", response_model=FirmSettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(FirmSettings).first()
    return settings


@router.put("/", response_model=FirmSettingsResponse)
def update_settings(data: FirmSettingsResponse, db: Session = Depends(get_db)):

    settings = db.query(FirmSettings).first()

    settings.auto_generate_draft = data.auto_generate_draft
    settings.auto_generate_risk = data.auto_generate_risk

    settings.draft_sla_days = data.draft_sla_days
    settings.review_sla_days = data.review_sla_days
    settings.submission_sla_days = data.submission_sla_days

    db.commit()
    db.refresh(settings)

    return settings