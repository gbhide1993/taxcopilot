import re

from fastapi import Request
from app.services.llm_service import generate_answer
from sqlalchemy.orm import Session, joinedload
from app.models.notice import Notice, NoticeStatus
from app.services.risk_service import calculate_and_store_risk
from app.models.notice_risk_metadata import NoticeRiskMetadata
from datetime import date
from sqlalchemy.orm import aliased
from app.models.sections_master import SectionsMaster
from app.models.user import User
from app.models.client import Client
from datetime import date
from app.services.risk_service import (
    get_risk_drivers,
    get_recommended_action,
    get_risk_severity
)
from sqlalchemy import func
from app.models.client import Client
from app.models.notice_timeline import NoticeTimeline  


def create_notice(
    db: Session,
    notice_data,
    created_by: int,
):
    clean_section = notice_data.section_reference.replace("Section", "").strip()
    normalized_section = f"Section {clean_section}"
    # 🔐 Validate section exists in master table

    section_exists = (
    db.query(SectionsMaster)
    .filter(
        SectionsMaster.act_name == notice_data.act_name,
        SectionsMaster.section_reference == normalized_section
    )
    .first()
    )

    if not section_exists:
        raise ValueError("Invalid section reference for selected Act.")

    # Save normalized value
    notice_data.section_reference = notice_data.section_reference.strip()

    notice = Notice(
        notice_number=notice_data.notice_number,
        notice_type=notice_data.notice_type.strip().replace(".", ""),
        description=notice_data.description,
        received_date=notice_data.received_date,
        due_date=notice_data.due_date,
        client_id=notice_data.client_id,
        created_by=created_by,
        section_reference=notice_data.section_reference.strip(),
        assessment_year=notice_data.assessment_year,
        act_name=notice_data.act_name,   # 🔥 USE REQUEST VALUE
    )

    db.add(notice)
    db.flush()

    # Risk calculation
    calculate_and_store_risk(db, notice.id)

    db.commit()
    db.refresh(notice)

    return notice
    
def extract_section(text: str):
    pattern = r"(?:section|sec\.?|u/s|under section)\s*([0-9]+[A-Za-z]?(?:\([0-9A-Za-z]+\))*)"
    
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return None



def extract_assessment_year(text: str):
    match = re.search(r"Assessment Year\s*[:\-]?\s*(\d{4}-\d{2})", text, re.IGNORECASE)
    return match.group(1) if match else None


def classify_notice_with_llm(text: str):

    prompt = f"""
You are an Indian tax expert.

Classify the following notice into one of these types:

- Scrutiny Notice
- Reassessment Notice
- Demand Notice
- Defective Return Notice
- Penalty Notice
- Other

Text:
{text[:2000]}

Respond with ONLY the notice type.
"""

    result = generate_answer(prompt)
    return result.strip()


def classify_notice(text: str):

    section = extract_section(text)
    assessment_year = extract_assessment_year(text)

    notice_type = None

    # Rule-based fast classification
    if section:
        if section.startswith("143"):
            notice_type = "Scrutiny Notice"
        elif section.startswith("148"):
            notice_type = "Reassessment Notice"
        elif section.startswith("156"):
            notice_type = "Demand Notice"
        elif section.startswith("139"):
            notice_type = "Defective Return Notice"
        elif section.startswith("271"):
            notice_type = "Penalty Notice"

    # Fallback to LLM
    if not notice_type:
        notice_type = classify_notice_with_llm(text)

    return {
        "notice_type": notice_type,
        "section_reference": section,
        "assessment_year": assessment_year
    }

def list_notices(
    db: Session,
    user_id: int,
    status: NoticeStatus = None,
    section: str = None,
    client_id: int = None,
    from_date: date = None,
    to_date: date = None,
    risk_level: str = None,
    unassigned_only: bool = False,
    overdue_only: bool = False,
    page: int = 1,
    page_size: int = 10,
):
    risk_alias = aliased(NoticeRiskMetadata)
    user_alias = aliased(User)

    base_query = (
        db.query(
        Notice,
        risk_alias.risk_score,
        user_alias.full_name.label("assigned_user_name"),
        Client.name.label("client_name")
        )
        .outerjoin(
            risk_alias,
            risk_alias.notice_id == Notice.id
        )
        .outerjoin(
            user_alias,
            user_alias.id == Notice.assigned_to
        )
        .outerjoin(
            Client,
            Client.id == Notice.client_id
        )
        .filter(Notice.created_by == user_id)
    )

    # Filters
    if status:
        base_query = base_query.filter(Notice.status == status)

    if section:
        base_query = base_query.filter(
            Notice.section_reference.ilike(f"%{section}%")
        )

    if client_id:
        base_query = base_query.filter(
            Notice.client_id == client_id
        )

    if from_date:
        base_query = base_query.filter(
            Notice.due_date >= from_date
        )

    if to_date:
        base_query = base_query.filter(
            Notice.due_date <= to_date
        )

    if risk_level:
        if risk_level == "high":
            base_query = base_query.filter(
                risk_alias.risk_score >= 3.5
            )
        elif risk_level == "medium":
            base_query = base_query.filter(
                risk_alias.risk_score >= 2,
                risk_alias.risk_score < 3.5
            )
        elif risk_level == "low":
            base_query = base_query.filter(
                risk_alias.risk_score < 2
            )
    # Unassigned filter
    if unassigned_only:
        base_query = base_query.filter(Notice.assigned_to == None)

    # Overdue filter
    if overdue_only:
        base_query = base_query.filter(Notice.due_date < date.today())

    # Count (no ordering)
    total = base_query.order_by(None).count()

    # Data query
    results = (
        base_query
        .order_by(
            risk_alias.risk_score.desc().nullslast(),
            Notice.id.desc()
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for notice, risk_score, assigned_user_name, client_name in results:

        score = float(risk_score) if risk_score else 0

        notice.risk_score = score
        notice.assigned_user_name = assigned_user_name
        notice.client_name = client_name

        notice.risk_drivers = get_risk_drivers(notice)
        notice.recommended_action = get_recommended_action(notice)
        notice.risk_severity = get_risk_severity(score)

        items.append(notice)

    

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }

def update_notice_status(db: Session, notice_id: int, status, user_id: int):
    notice = db.query(Notice).filter(
        Notice.id == notice_id,
        Notice.created_by == user_id
    ).first()

    if not notice:
        return None

    old_status = notice.status

    notice.status = NoticeStatus(status)

    db.add(
        NoticeTimeline(
            notice_id=notice.id,
            event_type="STATUS_CHANGE",
            description=f"Status changed from {old_status.value} to {status}",
            user_id=user_id
        )
    )

    # Recalculate risk
    calculate_and_store_risk(db, notice.id)

    db.commit()
    db.refresh(notice)

    return notice

def assign_notice(db, notice_id, assigned_to, user_id):

    notice = db.query(Notice).filter(Notice.id == notice_id).first()

    old_assignee = notice.assigned_to

    notice.assigned_to = assigned_to

    db.add(
        NoticeTimeline(
            notice_id = notice_id,
            event_type = "ASSIGNMENT_CHANGE",
            description = f"Assigned changed from {old_assignee} to {assigned_to}",
            user_id = user_id
        )
    )

    db.commit()

    return notice



def get_client_litigation_exposure(db):
    results = (
        db.query(
            Client.name.label("client_name"),
            func.count(Notice.id).label("notice_count")
        )
        .join(Notice, Notice.client_id == Client.id)
        .group_by(Client.name)
        .order_by(func.count(Notice.id).desc())
        .all()
    )

    return [
        {
            "client_name": r.client_name,
            "count": r.notice_count
        }
        for r in results
    ]