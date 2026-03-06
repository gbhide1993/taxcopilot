from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.report_service import get_reports_summary

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/")
def get_reports(
    db: Session = Depends(get_db)
):
    return get_reports_summary(db)