from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.intelligence_service import get_litigation_intelligence

router = APIRouter(prefix="/intelligence",
    tags=["Intelligence"])



@router.get("/")
def intelligence_dashboard(db: Session = Depends(get_db)):

    return get_litigation_intelligence(db)