from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.notice import Notice
from app.services.section_service import get_section_by_act_and_number
from app.models.draft_version import DraftVersion
from sqlalchemy import func, desc
from app.models.client import Client




def generate_structured_draft(db: Session, notice_id: int):

    # ---------------------------------
    # 1️⃣ Validate Notice Exists
    # ---------------------------------
    notice = db.query(Notice).filter(Notice.id == notice_id).first()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found."
        )

    # ---------------------------------
    # 2️⃣ Strict Grounding Validation
    # ---------------------------------

    if not notice.act_name or not notice.act_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Act name not defined for this notice. Cannot generate draft."
        )

    if not notice.section_reference or not notice.section_reference.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section reference not defined for this notice."
        )

    # Strict lookup in SectionsMaster
    section = get_section_by_act_and_number(
        db,
        notice.act_name.strip(),
        notice.section_reference.strip()
    )

    if not section:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section not grounded in master database."
        )

    # ---------------------------------
    # 3️⃣ Deterministic Draft Construction
    # ---------------------------------

    introduction = (
        f"This is in response to Notice No. {notice.notice_number} "
        f"issued under Section {section.section_reference} "
        f"of the {notice.act_name}."
    )

    facts_summary = (
        f"The notice dated {notice.received_date} pertains to "
        f"Assessment Year {notice.assessment_year or 'Not specified'}. "
        f"Brief description: {notice.description or 'N/A'}."
    )

    legal_position = (
        f"As per Section {section.section_reference} titled "
        f"'{section.heading}', the law provides as follows:\n\n"
        f"{section.heading}"
    )

    section_reference_display = (
        f"{section.section_reference} – {section.heading}"
    )

    prayer = (
        "In light of the above facts and legal position, "
        "it is respectfully requested that the proceedings "
        "initiated under the said notice be dropped."
    )

    # ---------------------------------
    # 4️⃣ Versioning Logic
    # ---------------------------------

    latest_version = (
        db.query(func.max(DraftVersion.version_number))
        .filter(DraftVersion.notice_id == notice.id)
        .scalar()
    )

    next_version = (latest_version or 0) + 1

    draft_version = DraftVersion(
        notice_id=notice.id,
        version_number=next_version,
        introduction=introduction,
        facts_summary=facts_summary,
        legal_position=legal_position,
        section_reference=section_reference_display,
        prayer=prayer
    )

    db.add(draft_version)
    db.commit()
    db.refresh(draft_version)

    # ---------------------------------
    # 5️⃣ Return Structured Response
    # ---------------------------------

    return {
        "notice_id": notice.id,
        "version_number": next_version,
        "introduction": introduction,
        "facts_summary": facts_summary,
        "legal_position": legal_position,
        "section_reference": section_reference_display,
        "prayer": prayer
    }


def get_latest_draft(db: Session, notice_id: int):

    draft = (
        db.query(DraftVersion)
        .filter(DraftVersion.notice_id == notice_id)
        .order_by(desc(DraftVersion.version_number))
        .first()
    )

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No drafts found for this notice."
        )

    return draft


def get_all_draft_versions(db: Session, notice_id: int):

    drafts = (
        db.query(DraftVersion)
        .filter(DraftVersion.notice_id == notice_id)
        .order_by(DraftVersion.version_number.asc())
        .all()
    )

    if not drafts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No drafts found for this notice."
        )

    return {
        "notice_id": notice_id,
        "versions": drafts
    }


def get_all_drafts(db: Session):

    results = (
        db.query(
            DraftVersion.id,
            DraftVersion.notice_id,
            DraftVersion.version_number,
            DraftVersion.created_at,
            Notice.notice_number,
            Notice.section_reference,
            Client.name.label("client_name")
        )
        .join(Notice, Notice.id == DraftVersion.notice_id)
        .join(Client, Client.id == Notice.client_id)
        .order_by(DraftVersion.created_at.desc())
        .all()
    )

    drafts = []

    for r in results:

        drafts.append({
            "id": r.id,
            "notice_id": r.notice_id,
            "version_number": r.version_number,
            "created_at": r.created_at,
            "notice_number": r.notice_number,
            "section_reference": r.section_reference,
            "client_name": r.client_name
        })

    return drafts