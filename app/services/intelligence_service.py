from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.notice import Notice
from app.models.notice_risk_metadata import NoticeRiskMetadata
from app.models.client import Client


def get_litigation_intelligence(db: Session):

    # ---------------------------
    # Most litigated sections
    # ---------------------------

    sections = (
        db.query(
            Notice.section_reference,
            func.count(Notice.id).label("count")
        )
        .group_by(Notice.section_reference)
        .order_by(func.count(Notice.id).desc())
        .limit(5)
        .all()
    )

    section_data = [
        {
            "section": s.section_reference or "Unknown",
            "count": s.count
        }
        for s in sections
    ]

    # ---------------------------
    # Clients generating notices
    # ---------------------------

    clients = (
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

    client_data = [
        {
            "client": c.name,
            "count": c.count
        }
        for c in clients
    ]

    # ---------------------------
    # Average resolution time
    # ---------------------------

    resolved = (
        db.query(Notice)
        .filter(Notice.status.in_(["closed", "replied"]))
        .all()
    )

    days = []

    for r in resolved:

        if r.received_date and r.due_date:
            diff = (r.due_date - r.received_date).days
            days.append(diff)

    avg_resolution = 0

    if days:
        avg_resolution = round(sum(days) / len(days))

    return {

        "top_sections": section_data,
        "top_clients": client_data,
        "avg_resolution_days": avg_resolution

    }