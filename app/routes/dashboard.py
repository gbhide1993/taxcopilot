from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import date

from app.database import get_db
from app.models.notice import Notice
from app.models.notice_risk_metadata import NoticeRiskMetadata
from app.models.firm import Firm

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def dashboard_view(
    request: Request,
    filter_by: str = Query(None),
    db: Session = Depends(get_db)
):

    today = date.today()

    base_query = db.query(Notice, NoticeRiskMetadata).join(
        NoticeRiskMetadata,
        Notice.id == NoticeRiskMetadata.notice_id
    )

    # -------------------
    # APPLY FILTERS
    # -------------------
    if filter_by == "open":
        base_query = base_query.filter(Notice.status == "open")

    elif filter_by == "in_progress":
        base_query = base_query.filter(Notice.status == "in_progress")

    elif filter_by == "replied":
        base_query = base_query.filter(Notice.status == "replied")

    elif filter_by == "closed":
        base_query = base_query.filter(Notice.status == "closed")

    elif filter_by == "overdue":
        base_query = base_query.filter(
            Notice.due_date < today,
            Notice.status != "closed"
        )

    elif filter_by == "high_risk":
        base_query = base_query.filter(
            NoticeRiskMetadata.risk_score >= 4
        )

    results = base_query.order_by(
        desc(NoticeRiskMetadata.risk_score)
    ).all()

    # -------------------
    # BUILD TABLE DATA
    # -------------------
    notice_list = []

    for notice, risk in results:
        notice_list.append({
            "id": notice.id,
            "notice_number": notice.notice_number,
            "client_id": notice.client_id,
            "section": notice.section_reference,
            "status": notice.status,
            "risk_score": round(risk.risk_score, 2),
            "days_remaining": risk.days_remaining,
        })

    # -------------------
    # METRICS
    # -------------------
        status_counts = dict(
                    db.query(
                        Notice.status,
                        func.count(Notice.id)
                    ).group_by(Notice.status).all()
                )

    open_count = status_counts.get("open", 0)
    in_progress_count = status_counts.get("in_progress", 0)
    replied_count = status_counts.get("replied", 0)
    closed_count = status_counts.get("closed", 0)

    total_active = open_count + in_progress_count + replied_count

    overdue_count = db.query(func.count(Notice.id)).filter(
        Notice.due_date < today,
        Notice.status != "closed"
    ).scalar()

    high_risk_count = db.query(func.count(NoticeRiskMetadata.notice_id)).filter(
        NoticeRiskMetadata.risk_score >= 4
    ).scalar()

    avg_risk = db.query(
        func.avg(NoticeRiskMetadata.risk_score)
    ).scalar() or 0

    firm = db.query(Firm).first()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "notice_list": notice_list,
            "total_active": total_active,
            "open_count": open_count,
            "in_progress_count": in_progress_count,
            "replied_count": replied_count,
            "closed_count": closed_count,
            "overdue_count": overdue_count,
            "high_risk_count": high_risk_count,
            "avg_risk": round(avg_risk, 2),
            "firm": firm,
            "current_filter": filter_by
        }
    )