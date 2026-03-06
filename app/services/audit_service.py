from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    user_id: int,
    role_name: str,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    details: dict | None = None
):
    audit_entry = AuditLog(
        user_id=user_id,
        role_name=role_name,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )

    db.add(audit_entry)
    db.commit()

def get_activity_logs(db):

    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(200)
        .all()
    )

    return logs