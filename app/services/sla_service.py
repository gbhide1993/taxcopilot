from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.notice import Notice
from app.models.draft_version import DraftVersion
from app.models.firm_settings import FirmSettings


def get_sla_monitor(db: Session):

    # Fetch firm settings
    settings = db.query(FirmSettings).first()

    # Fallback defaults if settings not present
    draft_sla = settings.draft_sla_days if settings else 2
    review_sla = settings.review_sla_days if settings else 1
    submission_sla = settings.submission_sla_days if settings else 1

    now = datetime.utcnow().date()

    draft_pending = 0
    review_pending = 0
    submission_pending = 0
    breached = 0

    notices = db.query(Notice).all()

    for notice in notices:

        if not notice.received_date:
            continue

        draft_deadline = notice.received_date + timedelta(days=draft_sla)

        draft = (
            db.query(DraftVersion)
            .filter(DraftVersion.notice_id == notice.id)
            .order_by(DraftVersion.created_at.desc())
            .first()
        )

        # Draft not created yet
        if not draft:

            draft_pending += 1

            if now > draft_deadline:
                breached += 1

        else:

            review_deadline = draft.created_at.date() + timedelta(days=review_sla)

            if now > review_deadline:
                review_pending += 1

        # Future logic placeholder
        # submission SLA will apply after review workflow is added

    return {
        "draft_pending": draft_pending,
        "review_pending": review_pending,
        "submission_pending": submission_pending,
        "breached": breached
    }