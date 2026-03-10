from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import timezone

from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.notice_timeline import NoticeTimeline
from app.models.user import User

router = APIRouter(
    prefix="/activity",
    tags=["Activity"]
)


@router.get("/")
def get_activity_logs(db: Session = Depends(get_db)):

    activity = []

    # -----------------------------
    # Fetch audit logs with user name
    # -----------------------------
    audit_logs = (
        db.query(AuditLog, User.full_name)
        .outerjoin(User, User.id == AuditLog.user_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(200)
        .all()
    )

    for log, user_name in audit_logs:

        ts = log.timestamp

        # Normalize timezone
        if ts is not None and ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        activity.append({
            "id": f"audit-{log.id}",
            "timestamp": ts,
            "user": user_name if user_name else f"User {log.user_id}",
            "action": log.action,
            "entity_type": log.entity_type,
            "details": log.details
        })

    # -----------------------------
    # Fetch notice timeline logs
    # -----------------------------
    notice_logs = (
        db.query(NoticeTimeline)
        .order_by(NoticeTimeline.created_at.desc())
        .limit(200)
        .all()
    )

    for n in notice_logs:

        ts = n.created_at

        if ts is not None and ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)

        user_name = "System"

        if n.user_id:
            user = db.query(User).filter(User.id == n.user_id).first()
            if user:
                user_name = user.full_name

        activity.append({
            "id": f"notice-{n.id}",
            "timestamp": ts,
            "user": user_name,
            "action": n.event_type,
            "entity_type": "Notice",
            "details": {
                "description": n.description
            }
        })

    # -----------------------------
    # Sort combined activity
    # -----------------------------
    activity.sort(
        key=lambda x: x["timestamp"] if x["timestamp"] else 0,
        reverse=True
    )

    return activity[:200]