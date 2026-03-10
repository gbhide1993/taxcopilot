from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.sla_service import get_sla_monitor

router = APIRouter(prefix="/sla", tags=["SLA"])


@router.get("/monitor")
def sla_monitor(db: Session = Depends(get_db)):
    return get_sla_monitor(db)