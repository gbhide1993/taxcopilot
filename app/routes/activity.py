from fastapi import APIRouter, Depends 
from sqlalchemy.orm import Session 
from app.database import get_db 
from app.models.audit_log import AuditLog 

router = APIRouter( 
    prefix="/activity", 
    tags=["Activity"] ) 

@router.get("/") 
def get_activity_logs(db: Session = Depends(get_db)): 
    logs = ( 
        db.query(AuditLog) 
        .order_by(AuditLog.timestamp.desc()) 
        .limit(200) 
        .all() ) 
    return logs