from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.risk_service import calculate_and_store_risk

router = APIRouter(
    prefix="/risk",
    tags=["Risk"]
)


@router.post("/calculate/{notice_id}")
def calculate_risk(
    notice_id: int,
    db: Session = Depends(get_db)
):
    return calculate_and_store_risk(db, notice_id)
