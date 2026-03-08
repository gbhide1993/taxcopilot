from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.workload_service import get_team_workload

router = APIRouter(prefix="/workload", tags=["Workload"])


@router.get("/")
def workload_monitor(db: Session = Depends(get_db)):
    return get_team_workload(db)