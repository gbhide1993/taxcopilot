from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.notice import Notice
from app.models.notice_risk_metadata import NoticeRiskMetadata
from app.models.client import Client


def get_reports_summary(db: Session):

    total_notices = db.query(func.count(Notice.id)).scalar()

    high_risk = (
        db.query(func.count(NoticeRiskMetadata.notice_id))
        .filter(NoticeRiskMetadata.risk_score >= 3)
        .scalar()
    )

    overdue = (
        db.query(func.count(Notice.id))
        .filter(Notice.status != "closed")
        .filter(Notice.due_date < func.now())
        .scalar()
    )

    client_distribution = (
        db.query(
            Client.name,
            func.count(Notice.id).label("count")
        )
        .join(Notice, Notice.client_id == Client.id)
        .group_by(Client.name)
        .all()
    )

    section_distribution = (
        db.query(
            Notice.section_reference,
            func.count(Notice.id).label("count")
        )
        .group_by(Notice.section_reference)
        .all()
    )

    return {
        "total_notices": total_notices,
        "high_risk": high_risk,
        "overdue": overdue,
        "client_distribution": [
            {"client": r.name, "count": r.count} for r in client_distribution
        ],
        "section_distribution": [
            {"section": r.section_reference, "count": r.count}
            for r in section_distribution
        ]
    }