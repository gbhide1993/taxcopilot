from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.risk_service import calculate_and_store_risk
from app.dependencies.auth import get_current_user
from sqlalchemy import desc
from datetime import date, timedelta

router = APIRouter(
    prefix="/risk",
    tags=["Risk"]
)


@router.post("/calculate/{notice_id}")
def calculate_risk(
    notice_id: int,
    db: Session = Depends(get_db)
):
    return calculate_and_store_risk(db, notice_id)

from datetime import date
from sqlalchemy import func, desc
from app.models.notice import Notice
from app.models.notice_risk_metadata import NoticeRiskMetadata

@router.get("/monitor")
def risk_monitor(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    today = date.today()

    base_query = (
        db.query(Notice)
        .filter(Notice.created_by == current_user.id)
    )

    total = base_query.count()

    high = (
        db.query(func.count(Notice.id))
        .join(NoticeRiskMetadata)
        .filter(
            Notice.created_by == current_user.id,
            NoticeRiskMetadata.risk_score >= 4
        )
        .scalar()
    )

    medium = (
        db.query(func.count(Notice.id))
        .join(NoticeRiskMetadata)
        .filter(
            Notice.created_by == current_user.id,
            NoticeRiskMetadata.risk_score >= 2.5,
            NoticeRiskMetadata.risk_score < 4
        )
        .scalar()
    )

    low = (
        db.query(func.count(Notice.id))
        .join(NoticeRiskMetadata)
        .filter(
            Notice.created_by == current_user.id,
            NoticeRiskMetadata.risk_score < 2.5
        )
        .scalar()
    )

    overdue_high = (
        db.query(func.count(Notice.id))
        .join(NoticeRiskMetadata)
        .filter(
            Notice.created_by == current_user.id,
            Notice.due_date < today,
            NoticeRiskMetadata.risk_score >= 4
        )
        .scalar()
    )

    # Top 10 risky notices
    top_notices = (
        db.query(Notice, NoticeRiskMetadata)
        .join(NoticeRiskMetadata)
        .filter(Notice.created_by == current_user.id)
        .order_by(desc(NoticeRiskMetadata.risk_score))
        .limit(10)
        .all()
    )

    return {
        "total": total or 0,
        "high": high or 0,
        "medium": medium or 0,
        "low": low or 0,
        "overdue_high": overdue_high or 0,
        "top_notices": [
            {
                "notice_id": n.id,
                "notice_number": n.notice_number,
                "due_date": n.due_date,
                "risk_score": r.risk_score
            }
            for n, r in top_notices
        ]
    }

@router.get("/work-queue")
def work_queue(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    today = date.today()
    soon = today + timedelta(days=3)

    results = (
        db.query(Notice, NoticeRiskMetadata)
        .join(NoticeRiskMetadata)
        .filter(Notice.created_by == current_user.id)
        .all()
    )

    queue = []

    for notice, risk in results:
        priority = 4  # default lowest

        if notice.due_date < today and risk.risk_score >= 4:
            priority = 1
        elif risk.risk_score >= 4:
            priority = 2
        elif notice.due_date <= soon:
            priority = 3
        elif risk.risk_score >= 2.5:
            priority = 4

        queue.append({
            "notice_id": notice.id,
            "notice_number": notice.notice_number,
            "due_date": notice.due_date,
            "risk_score": risk.risk_score,
            "priority": priority
        })

    queue = sorted(queue, key=lambda x: x["priority"])

    return queue[:20]