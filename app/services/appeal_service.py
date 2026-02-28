from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException
from datetime import datetime

from app.models.notice import Notice
from app.models.draft_version import DraftVersion
from app.models.notice_risk_metadata import NoticeRiskMetadata
from app.models.appeal_versions import AppealVersion


def generate_appeal(db: Session, notice_id: int):

    notice = db.query(Notice).filter(Notice.id == notice_id).first()

    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found.")

    draft = (
        db.query(DraftVersion)
        .filter(DraftVersion.notice_id == notice_id)
        .order_by(DraftVersion.version_number.desc())
        .first()
    )

    if not draft:
        raise HTTPException(status_code=400, detail="No draft available to base appeal on.")

    risk = db.query(NoticeRiskMetadata).filter(
        NoticeRiskMetadata.notice_id == notice_id
    ).first()

    severity = risk.severity_score if risk else 3

    # ==========================
    # Background Section
    # ==========================
    background = (
        f"The present appeal arises from proceedings initiated under "
        f"{notice.section_reference} of the {notice.act_name}. "
        f"The Appellant submits that the impugned notice and subsequent "
        f"proceedings suffer from serious legal and procedural infirmities."
    )

    # ==========================
    # Grounds of Appeal (Numbered)
    # ==========================
    grounds_list = []

    grounds_list.append(
        "1. That the impugned notice is bad in law and without jurisdiction."
    )

    grounds_list.append(
        "2. That the mandatory conditions precedent for invoking the said section were not fulfilled."
    )

    if severity >= 4:
        grounds_list.append(
            "3. That there is complete absence of tangible material to justify the initiation of proceedings."
        )
    else:
        grounds_list.append(
            "3. That the formation of belief is arbitrary and without proper application of mind."
        )

    grounds_list.append(
        "4. That the principles of natural justice have been violated."
    )

    grounds_list.append(
        "5. That the additions proposed are unsustainable both on facts and in law."
    )

    grounds = "\n\n".join(grounds_list)

    # ==========================
    # Prayer
    # ==========================
    prayer = (
        "In view of the above grounds, it is most respectfully prayed that "
        "the impugned notice and proceedings be quashed and appropriate relief "
        "be granted to the Appellant."
    )

    # ==========================
    # Versioning Logic
    # ==========================
    latest_version = db.query(
        func.max(AppealVersion.version_number)
    ).filter(
        AppealVersion.notice_id == notice_id
    ).scalar()

    next_version = 1 if latest_version is None else latest_version + 1

    appeal = AppealVersion(
        notice_id=notice_id,
        version_number=next_version,
        background=background,
        grounds=grounds,
        prayer=prayer
    )

    db.add(appeal)
    db.commit()
    db.refresh(appeal)

    return appeal


def get_latest_appeal(db: Session, notice_id: int):

    appeal = (
        db.query(AppealVersion)
        .filter(AppealVersion.notice_id == notice_id)
        .order_by(desc(AppealVersion.version_number))
        .first()
    )

    if not appeal:
        raise HTTPException(status_code=404, detail="No appeal found.")

    return appeal


def get_all_appeal_versions(db: Session, notice_id: int):

    appeals = (
        db.query(AppealVersion)
        .filter(AppealVersion.notice_id == notice_id)
        .order_by(AppealVersion.version_number)
        .all()
    )

    if not appeals:
        raise HTTPException(status_code=404, detail="No appeals found.")

    return appeals
