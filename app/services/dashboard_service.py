from sqlalchemy.orm import Session
from sqlalchemy import func, desc, case
from datetime import date, timedelta

from app.models.notice import Notice
from app.models.client import Client
from app.models.user import User
from app.models.notice_risk_metadata import NoticeRiskMetadata


def get_dashboard_summary(db: Session):

    today = date.today()
    next_week = today + timedelta(days=7)

    # --------------------------------------------------
    # BASIC METRICS
    # --------------------------------------------------

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

    # --------------------------------------------------
    # TOP CLIENTS BY NOTICE COUNT
    # --------------------------------------------------

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

    # --------------------------------------------------
    # URGENT NOTICES (HIGH RISK + EARLY DEADLINES)
    # --------------------------------------------------

    urgent_notices = (
        db.query(
            Notice.id,
            Client.name.label("client"),
            Notice.section_reference.label("section"),
            NoticeRiskMetadata.risk_score.label("risk"),
            Notice.due_date
        )
        .join(Client, Notice.client_id == Client.id)
        .join(
            NoticeRiskMetadata,
            Notice.id == NoticeRiskMetadata.notice_id
        )
        .filter(Notice.status != "closed")
        .order_by(
            desc(NoticeRiskMetadata.risk_score),
            Notice.due_date
        )
        .limit(5)
        .all()
    )

    urgent_data = [
        {
            "id": r.id,
            "client": r.client,
            "section": r.section,
            "risk": round(r.risk, 2),
            "due": str(r.due_date)
        }
        for r in urgent_notices
    ]

    # --------------------------------------------------
    # PIPELINE STATUS
    # --------------------------------------------------

    status_counts = dict(
        db.query(
            Notice.status,
            func.count(Notice.id)
        ).group_by(Notice.status).all()
    )

    pipeline = {
        "open": status_counts.get("open", 0),
        "in_progress": status_counts.get("in_progress", 0),
        "replied": status_counts.get("replied", 0),
        "closed": status_counts.get("closed", 0),
    }

    # --------------------------------------------------
    # TEAM WORKLOAD
    # --------------------------------------------------

    workload_query = (
        db.query(
            User.full_name.label("ca"),
            func.count(Notice.id).label("count")
        )
        .join(Notice, Notice.assigned_to == User.id)
        .filter(Notice.status != "closed")
        .group_by(User.full_name)
        .order_by(desc(func.count(Notice.id)))
        .limit(5)
        .all()
    )

    workload = [
        {
            "ca": r.ca,
            "count": r.count
        }
        for r in workload_query
    ]

    # --------------------------------------------------
    # CLIENT RISK HEAT TABLE
    # --------------------------------------------------

    client_risk_query = (
        db.query(
            Client.name.label("client"),
            func.count(Notice.id).label("notices"),

            func.sum(
                case(
                    (NoticeRiskMetadata.risk_score >= 4, 1),
                    else_=0
                )
            ).label("critical"),

            func.sum(
                case(
                    (
                        (NoticeRiskMetadata.risk_score >= 3)
                        & (NoticeRiskMetadata.risk_score < 4),
                        1
                    ),
                    else_=0
                )
            ).label("high"),

            func.sum(
                case(
                    (
                        (NoticeRiskMetadata.risk_score >= 2)
                        & (NoticeRiskMetadata.risk_score < 3),
                        1
                    ),
                    else_=0
                )
            ).label("medium"),

            func.sum(
                case(
                    (NoticeRiskMetadata.risk_score < 2, 1),
                    else_=0
                )
            ).label("low"),
        )
        .join(Notice, Notice.client_id == Client.id)
        .join(
            NoticeRiskMetadata,
            Notice.id == NoticeRiskMetadata.notice_id
        )
        .group_by(Client.name)
        .order_by(desc(func.count(Notice.id)))
        .limit(10)
        .all()
    )

    client_risk = [
        {
            "client": r.client,
            "notices": r.notices,
            "critical": int(r.critical or 0),
            "high": int(r.high or 0),
            "medium": int(r.medium or 0),
            "low": int(r.low or 0),
        }
        for r in client_risk_query
    ]

    # --------------------------------------------------
    # NEXT 7 DAYS DEADLINE BOARD
    # --------------------------------------------------

    deadline_query = (
        db.query(
            Notice.id,
            Client.name.label("client"),
            Notice.notice_number,
            Notice.section_reference,
            Notice.due_date
        )
        .join(Client, Notice.client_id == Client.id)
        .filter(
            Notice.due_date >= today,
            Notice.due_date <= next_week,
            Notice.status != "closed"
        )
        .order_by(Notice.due_date)
        .limit(10)
        .all()
    )

    deadline_board = [
        {
            "id": r.id,
            "client": r.client,
            "notice_number": r.notice_number,
            "section": r.section_reference,
            "due": str(r.due_date)
        }
        for r in deadline_query
    ]

    # --------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------

    return {

        "total_notices": total_notices,
        "high_risk": high_risk,
        "overdue": overdue,
        "unassigned": unassigned,

        "top_clients": [
            {"client": r.name, "count": r.count}
            for r in top_clients
        ],

        "urgent_notices": urgent_data,
        "pipeline": pipeline,
        "workload": workload,

        "client_risk": client_risk,
        "deadline_board": deadline_board
    }