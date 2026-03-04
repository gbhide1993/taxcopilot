from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from fastapi import HTTPException, status
from datetime import datetime
from app.models.notice import Notice
from app.models.sections_master import SectionsMaster
from app.models.draft_version import DraftVersion
from app.models.notice_risk_metadata import NoticeRiskMetadata  # create model
from app.services.section_service import get_section_by_act_and_number


def calculate_urgency_weight(days_remaining: int) -> int:

    if days_remaining <= 3:
        return 5
    elif days_remaining <= 7:
        return 4
    elif days_remaining <= 15:
        return 3
    elif days_remaining <= 30:
        return 2
    else:
        return 1


def calculate_status_weight(status: str) -> int:

    mapping = {
        "open": 5,
        "in_progress": 3,
        "replied": 2,
        "closed": 1
    }

    return mapping.get(status, 3)


def calculate_repeat_flag(db: Session, notice: Notice) -> bool:

    count = (
        db.query(func.count(Notice.id))
        .filter(
            Notice.client_id == notice.client_id,
            Notice.section_reference == notice.section_reference,
            Notice.id != notice.id
        )
        .scalar()
    )

    return count > 0


def calculate_and_store_risk(db: Session, notice_id: int):

    notice = db.query(Notice).filter(Notice.id == notice_id).first()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found."
        )


    section = get_section_by_act_and_number(
        db,
        notice.act_name,
        notice.section_reference
    )

    if not section:
        return {
            "score": None,
            "message": "Section not grounded yet"
        }

    severity_score = section.severity_level

    today = date.today()
    days_remaining = (notice.due_date - today).days

    urgency_weight = 5 if days_remaining <= 3 else \
                     4 if days_remaining <= 7 else \
                     3 if days_remaining <= 15 else \
                     2 if days_remaining <= 30 else 1

    status_map = {
        "open": 5,
        "in_progress": 3,
        "replied": 2,
        "closed": 1
    }

    status_weight = status_map.get(notice.status.value, 3)

    repeat_count = (
        db.query(func.count(Notice.id))
        .filter(
            Notice.client_id == notice.client_id,
            Notice.section_reference == notice.section_reference,
            Notice.id != notice.id
        )
        .scalar()
    )

    repeat_weight = 5 if repeat_count > 0 else 1

    risk_score = round(
        (severity_score * 0.4) +
        (urgency_weight * 0.3) +
        (status_weight * 0.2) +
        (repeat_weight * 0.1),
        2
    )

    existing = db.query(NoticeRiskMetadata).filter(
        NoticeRiskMetadata.notice_id == notice.id
    ).first()

    if existing:
        existing.severity_score = severity_score
        existing.days_remaining = days_remaining
        existing.repeat_flag = repeat_count > 0
        existing.risk_score = risk_score
        existing.last_updated = datetime.utcnow()
    else:
        db.add(
            NoticeRiskMetadata(
                notice_id=notice.id,
                severity_score=severity_score,
                days_remaining=days_remaining,
                repeat_flag=repeat_count > 0,
                risk_score=risk_score,
                last_updated=datetime.utcnow()
            )
        )

    db.commit()

    return {
        "score": risk_score,
        "severity": severity_score,
        "days_remaining": days_remaining,
        "repeat_flag": repeat_count > 0
    }

def get_risk_summary(db: Session):

    today = date.today()

    total_notices = db.query(func.count()).select_from(Notice).scalar()

    overdue_count = (
        db.query(func.count())
        .select_from(Notice)
        .filter(Notice.due_date < today)
        .scalar()
    )

    open_count = (
        db.query(func.count())
        .select_from(Notice)
        .filter(Notice.status == "open")
        .scalar()
    )

    high_risk_count = (
        db.query(func.count())
        .select_from(NoticeRiskMetadata)
        .filter(NoticeRiskMetadata.risk_score >= 3.5)
        .scalar()
    )

    avg_risk_score = (
        db.query(func.avg(NoticeRiskMetadata.risk_score))
        .scalar()
    )

    return {
        "total_notices": total_notices or 0,
        "overdue_count": overdue_count or 0,
        "open_count": open_count or 0,
        "high_risk_count": high_risk_count or 0,
        "average_risk_score": round(avg_risk_score or 0, 2)
    }

def get_section_distribution(db: Session):

    results = (
        db.query(
            Notice.act_name,
            Notice.section_reference,
            func.count(Notice.id).label("notice_count")
        )
        .filter(Notice.section_reference != "UNKNOWN")
        .group_by(Notice.act_name, Notice.section_reference)
        .all()
    )

    return [
        {
            "act_name": r.act_name,
            "section_reference": r.section_reference,
            "notice_count": r.notice_count
        }
        for r in results
    ]
