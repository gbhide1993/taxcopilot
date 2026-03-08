from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.deadline_service import get_deadline_alerts

router = APIRouter(prefix="/deadlines", tags=["Deadlines"])


@router.get("/")
def deadline_monitor(db: Session = Depends(get_db)):
    return get_deadline_alerts(db)