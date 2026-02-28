from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.notice import Notice
from app.services.section_service import get_section_by_act_and_number
from app.models.draft_version import DraftVersion
from sqlalchemy import func, desc



def generate_structured_draft(db: Session, notice_id: int):

    notice = db.query(Notice).filter(Notice.id == notice_id).first()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found."
        )

    if notice.section_reference == "UNKNOWN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notice section is not properly defined."
        )

    # Strict grounding lookup
    section = get_section_by_act_and_number(
        db,
        notice.act_name,
        notice.section_reference
    )

    # Deterministic Draft Construction
    introduction = (
        f"This is in response to Notice No. {notice.notice_number} "
        f"issued under {notice.section_reference} of the "
        f"{notice.act_name}."
    )

    facts_summary = (
        f"The notice dated {notice.received_date} pertains to "
        f"Assessment Year {notice.assessment_year or 'Not specified'}. "
        f"Brief description: {notice.description or 'N/A'}."
    )

    legal_position = (
        f"As per {section.section_reference} titled "
        f"'{section.heading}', the law states:\n\n"
        f"{section.heading}"
    )

    section_reference = (
        f"{section.section_reference} – {section.heading}"
    )

    prayer = (
        "In light of the above facts and legal position, "
        "it is respectfully requested that the proceedings "
        "initiated under the said notice be dropped."
    )

     # Determine next version number
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
        section_reference=section_reference,
        prayer=prayer
    )

    db.add(draft_version)
    db.commit()
    db.refresh(draft_version)

    return {
        "notice_id": notice.id,
        "version_number": next_version,
        "introduction": introduction,
        "facts_summary": facts_summary,
        "legal_position": legal_position,
        "section_reference": section_reference,
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
