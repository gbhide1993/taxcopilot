from sqlalchemy.orm import Session
from datetime import date
from app.models.notice import Notice


def get_deadline_alerts(db: Session):

    today = date.today()

    notices = db.query(Notice).all()

    overdue = 0
    due_today = 0
    due_3_days = 0
    due_7_days = 0
    safe = 0

    for n in notices:

        if not n.due_date:
            continue

        days_left = (n.due_date - today).days

        if days_left < 0:
            overdue += 1

        elif days_left == 0:
            due_today += 1

        elif days_left <= 3:
            due_3_days += 1

        elif days_left <= 7:
            due_7_days += 1

        else:
            safe += 1

    return {
        "overdue": overdue,
        "due_today": due_today,
        "due_3_days": due_3_days,
        "due_7_days": due_7_days,
        "safe": safe
    }