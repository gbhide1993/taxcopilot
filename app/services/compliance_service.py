from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from app.models.notice import Notice
from app.models.notice_risk_metadata import NoticeRiskMetadata


def get_client_compliance_summary(db: Session, client_id: int):

    total_notices = (
        db.query(func.count())
        .select_from(Notice)
        .filter(Notice.client_id == client_id)
        .scalar()
    )

    if total_notices == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No notices found for this client."
        )

    # Status distribution
    status_distribution = (
        db.query(
            Notice.status,
            func.count(Notice.id).label("count")
        )
        .filter(Notice.client_id == client_id)
        .group_by(Notice.status)
        .all()
    )

    # Section frequency
    section_frequency = (
        db.query(
            Notice.section_reference,
            func.count(Notice.id).label("count")
        )
        .filter(
            Notice.client_id == client_id,
            Notice.section_reference != "UNKNOWN"
        )
        .group_by(Notice.section_reference)
        .all()
    )

    # Risk data
    avg_risk_score = (
        db.query(func.avg(NoticeRiskMetadata.risk_score))
        .join(Notice, Notice.id == NoticeRiskMetadata.notice_id)
        .filter(Notice.client_id == client_id)
        .scalar()
    )

    high_risk_count = (
        db.query(func.count())
        .select_from(NoticeRiskMetadata)
        .join(Notice, Notice.id == NoticeRiskMetadata.notice_id)
        .filter(
            Notice.client_id == client_id,
            NoticeRiskMetadata.risk_score >= 3.5
        )
        .scalar()
    )

    return {
        "client_id": client_id,
        "total_notices": total_notices,
        "status_distribution": [
            {"status": s.status.value, "count": s.count}
            for s in status_distribution
        ],
        "section_frequency": [
            {"section_reference": s.section_reference, "count": s.count}
            for s in section_frequency
        ],
        "average_risk_score": round(avg_risk_score or 0, 2),
        "high_risk_count": high_risk_count or 0
    }
