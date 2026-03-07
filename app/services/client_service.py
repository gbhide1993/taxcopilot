from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.client import Client
from app.models.notice import Notice
from app.models.notice_risk_metadata import NoticeRiskMetadata
from app.models.draft_version import DraftVersion
from app.models.appeal_versions import AppealVersion


# ----------------------------------------------------
# CREATE CLIENT
# ----------------------------------------------------

def create_client(db: Session, client, user_id):

    new_client = Client(
        name=client.name,
        pan=client.pan,
        email=client.email,
        phone=client.phone,
        assigned_to=user_id
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return new_client


# ----------------------------------------------------
# UPDATE CLIENT
# ----------------------------------------------------

def update_client(db: Session, client_id, client_data, user_id):

    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        return None

    client.name = client_data.name
    client.pan = client_data.pan
    client.email = client_data.email
    client.phone = client_data.phone
    client.assigned_to = user_id

    db.commit()
    db.refresh(client)

    return client


# ----------------------------------------------------
# GET CLIENT LIST (NOTICE COUNT + RISK)
# ----------------------------------------------------

def get_clients(db: Session):

    results = (
        db.query(
            Client.id,
            Client.name,
            Client.pan,
            Client.email,
            Client.phone,
            Client.assigned_to,

            func.count(Notice.id).label("notice_count"),
            func.avg(NoticeRiskMetadata.risk_score).label("risk_score")
        )
        .outerjoin(Notice, Notice.client_id == Client.id)
        .outerjoin(
            NoticeRiskMetadata,
            NoticeRiskMetadata.notice_id == Notice.id
        )
        .group_by(Client.id)
        .order_by(Client.name)
        .all()
    )

    clients = []

    for r in results:

        risk_level = "Low"

        if r.risk_score:

            if r.risk_score >= 4:
                risk_level = "Critical"
            elif r.risk_score >= 3:
                risk_level = "High"
            elif r.risk_score >= 2:
                risk_level = "Medium"

        clients.append({
            "id": r.id,
            "name": r.name,
            "pan": r.pan,
            "email": r.email,
            "phone": r.phone,
            "assigned_to": r.assigned_to,
            "notice_count": int(r.notice_count or 0),
            "risk_exposure": risk_level
        })

    return clients


# ----------------------------------------------------
# CLIENT NOTICE HISTORY
# ----------------------------------------------------

def get_client_notice_history(db: Session, client_id: int):

    notices = (
        db.query(Notice)
        .filter(Notice.client_id == client_id)
        .order_by(Notice.received_date.desc())
        .all()
    )

    return [
        {
            "id": n.id,
            "notice_number": n.notice_number,
            "section": n.section_reference,
            "status": n.status,
            "received_date": str(n.received_date),
            "due_date": str(n.due_date)
        }
        for n in notices
    ]


# ----------------------------------------------------
# CLIENT COMPLIANCE SUMMARY (DRAWER)
# ----------------------------------------------------

def get_client_compliance_summary(client_id: int, db: Session):

    # -------------------
    # Notices
    # -------------------

    notices = (
        db.query(
            Notice.id,
            Notice.notice_number,
            Notice.section_reference,
            Notice.status,
            Notice.received_date,
            Notice.due_date
        )
        .filter(Notice.client_id == client_id)
        .order_by(Notice.received_date.desc())
        .all()
    )

    notice_data = [
        {
            "id": n.id,
            "notice_number": n.notice_number,
            "section": n.section_reference,
            "status": n.status,
            "received_date": str(n.received_date),
            "due_date": str(n.due_date)
        }
        for n in notices
    ]

    # -------------------
    # Drafts
    # -------------------

    drafts = (
        db.query(
            DraftVersion.id,
            DraftVersion.version_number,
            DraftVersion.created_at,
            Notice.notice_number
        )
        .join(Notice, Notice.id == DraftVersion.notice_id)
        .filter(Notice.client_id == client_id)
        .order_by(DraftVersion.created_at.desc())
        .all()
    )

    draft_data = [
        {
            "id": d.id,
            "notice_number": d.notice_number,
            "version": d.version_number,
            "created_at": str(d.created_at)
        }
        for d in drafts
    ]

    # -------------------
    # Appeals
    # -------------------

    appeals = (
        db.query(
            AppealVersion.id,
            AppealVersion.version_number,
            AppealVersion.created_at,
            Notice.notice_number
        )
        .join(Notice, Notice.id == AppealVersion.notice_id)
        .filter(Notice.client_id == client_id)
        .order_by(AppealVersion.created_at.desc())
        .all()
    )

    appeal_data = [
        {
            "id": a.id,
            "notice_number": a.notice_number,
            "version": a.version_number,
            "created_at": str(a.created_at)
        }
        for a in appeals
    ]

    return {
        "notices": notice_data,
        "drafts": draft_data,
        "appeals": appeal_data
    }