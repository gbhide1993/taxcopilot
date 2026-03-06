from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.models.notice import Notice
from app.models.client import Client
from app.models.notice_risk_metadata import NoticeRiskMetadata


def get_dashboard_summary(db: Session):

    today = date.today()

    total_notices = db.query(func.count(Notice.id)).scalar()

    high_risk = (
        db.query(func.count(NoticeRiskMetadata.notice_id))
        .filter(NoticeRiskMetadata.risk_score >= 3)
        .scalar()
    )

    overdue = (
        db.query(func.count(Notice.id))
        .filter(Notice.due_date < today)
        .filter(Notice.status != "closed")
        .scalar()
    )

    unassigned = (
        db.query(func.count(Notice.id))
        .filter(Notice.assigned_to == None)
        .scalar()
    )

    top_clients = (
        db.query(
            Client.name,
            func.count(Notice.id).label("count")
        )
        .join(Notice, Notice.client_id == Client.id)
        .group_by(Client.name)
        .order_by(func.count(Notice.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_notices": total_notices,
        "high_risk": high_risk,
        "overdue": overdue,
        "unassigned": unassigned,
        "top_clients": [
            {"client": r.name, "count": r.count}
            for r in top_clients
        ]
    }