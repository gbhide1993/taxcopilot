from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.services.embedding_service import generate_embedding
from app.models import Document, DocumentChunk, Notice, User, License
from app.dependencies.role_guard import require_role
from app.dependencies.auth import get_current_user
from datetime import date


router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health")
def system_health(db: Session = Depends(get_db)):

    # 1️⃣ Database check
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    # 2️⃣ Model check (lightweight test)
    try:
        _ = generate_embedding("health check")
        model_status = "loaded"
    except Exception:
        model_status = "error"

    # 3️⃣ Counts
    document_count = db.query(Document).count()
    chunk_count = db.query(DocumentChunk).count()
    notice_count = db.query(Notice).count()
    user_count = db.query(User).count()

    return {
        "database_status": db_status,
        "embedding_model_status": model_status,
        "documents": document_count,
        "document_chunks": chunk_count,
        "notices": notice_count,
        "users": user_count
    }



@router.get("/license")
def get_license_status(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["ADMIN"]))
):
    license = db.query(License).first()

    if not license:
        raise HTTPException(status_code=404, detail="License not found")

    current_users = db.query(User).count()

    today = date.today()
    days_remaining = (license.expiry_date - today).days

    expiry_warning = days_remaining <= 7
    is_active = license.is_active and days_remaining >= 0

    return {
        "is_active": is_active,
        "expiry_date": license.expiry_date,
        "days_remaining": days_remaining,
        "expiry_warning": expiry_warning,
        "max_users": license.max_users,
        "current_users": current_users,
        "remaining_slots": max(0, license.max_users - current_users)
    }

