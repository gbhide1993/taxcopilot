from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.notice import Notice
from app.models.user import User


def get_team_workload(db: Session):

    results = (
        db.query(
            User.name.label("ca"),
            func.count(Notice.id).label("count")
        )
        .join(Notice, Notice.assigned_to == User.id)
        .filter(Notice.status != "Closed")
        .group_by(User.name)
        .all()
    )

    workload = [
        {
            "ca": r.ca,
            "count": r.count
        }
        for r in results
    ]

    # Count unassigned notices
    unassigned = (
        db.query(func.count(Notice.id))
        .filter(Notice.assigned_to == None)
        .filter(Notice.status != "Closed")
        .scalar()
    )

    if unassigned:
        workload.append({
            "ca": "Unassigned",
            "count": unassigned
        })

    return workload