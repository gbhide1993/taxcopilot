import os
import re
import fitz
from datetime import date, timedelta

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Form,
)
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.role_guard import require_role
from app.dependencies.license_guard import check_license

from app.models.notice import NoticeStatus, Notice
from app.models.notice_timeline import NoticeTimeline
from app.models.user import User
from app.models.sections_master import SectionsMaster
from app.models.notice_risk_metadata import NoticeRiskMetadata

from app.schemas.notice_schema import (
    NoticeCreate,
    NoticeUpdateStatus,
    NoticeAssign,
    NoticeResponse,
)
from app.schemas.assignment_schema import (
    AssignNoticeResponse,
)

from app.services.notice_service import (
    create_notice,
    list_notices,
    update_notice_status as update_notice_status_service,
    classify_notice,
)
from app.services.assignment_service import assign_notice
from app.services.notice_parser_service import (
    extract_section,
    extract_assessment_year,
    extract_dates,
)

router = APIRouter(prefix="/notices", tags=["Notices"])


# ---------------------------------------------------------
# 📘 Create Notice (Manual)
# ---------------------------------------------------------
@router.post("/", response_model=NoticeResponse)
def create_new_notice(
    notice: NoticeCreate,
    db: Session = Depends(get_db),
    firm=Depends(check_license),
    current_user=Depends(get_current_user),
):
    # Optional classification hook
    classification = classify_notice(notice.description or "")

    return create_notice(
        db=db,
        notice_data=notice,
        created_by=current_user.id,
    )


# ---------------------------------------------------------
# 📘 Upload Notice PDF + Auto Classify
# ---------------------------------------------------------
@router.post("/upload")
def upload_notice(
    client_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    firm=Depends(check_license),
    current_user=Depends(require_role(["ADMIN", "SENIOR_CA"])),
):
    try:
        contents = file.file.read()
        pdf = fitz.open(stream=contents, filetype="pdf")

        extracted_text = ""
        for page in pdf:
            extracted_text += page.get_text()

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Unable to extract text from PDF.",
            )

        sections = db.query(SectionsMaster.section_reference).all()
        valid_sections = {s[0] for s in sections}

        # -----------------------------------------
        # Load valid sections from master
        # -----------------------------------------

        sections = db.query(SectionsMaster.section_reference).all()

        valid_sections = {
            re.sub(r"^Section\s+", "", s[0]).strip()
            for s in sections
        }

        # -----------------------------------------
        # Extract section using validated extraction
        # -----------------------------------------

        section_reference = extract_section(
            extracted_text,
            valid_sections
        )

        assessment_year = extract_assessment_year(extracted_text)
        received_date, due_date = extract_dates(extracted_text)

        if not received_date:
            received_date = date.today()

        if not due_date:
            due_date = received_date + timedelta(days=30)

        notice = Notice(
            notice_number=file.filename,
            notice_type="Income Tax Notice",
            act_name="Income Tax Act 2025",
            section_reference=section_reference,
            assessment_year=assessment_year,
            description="Auto-classified notice",
            received_date=received_date,
            due_date=due_date,
            status="open",
            client_id=client_id,
            created_by=current_user.id,
            assigned_to=None,
            raw_text=extracted_text,
        )

        db.add(notice)
        db.commit()
        db.refresh(notice)

        return {
            "message": "Notice uploaded and classified successfully",
            "notice_id": notice.id,
            "section_reference": section_reference,
            "assessment_year": assessment_year,
            "received_date": str(received_date),
            "due_date": str(due_date),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# 📘 List Notices (Paginated + Filters)
# ---------------------------------------------------------
@router.get("/")
def get_notices(
    status: NoticeStatus = Query(None),
    section: str = Query(None),
    client_id: int = Query(None),
    from_date: date = Query(None),
    to_date: date = Query(None),
    risk_level: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_notices(
        db=db,
        user_id=current_user.id,
        status=status,
        section=section,
        client_id=client_id,
        risk_level=risk_level,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size,
    )


# ---------------------------------------------------------
# 📘 Update Notice Status (PUT - Returns Full Notice)
# ---------------------------------------------------------
@router.put("/{notice_id}/status", response_model=NoticeResponse)
def change_status(
    notice_id: int,
    data: NoticeUpdateStatus,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated = update_notice_status_service(
        db,
        notice_id,
        data.status,
        current_user.id,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Notice not found")

    return updated


# ---------------------------------------------------------
# 📘 Assign Notice (Uses Assignment Service)
# ---------------------------------------------------------

@router.put("/{notice_id}/assign", response_model=AssignNoticeResponse)
def assign(
    notice_id: int,
    data: NoticeAssign,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated = assign_notice(
        db,
        notice_id,
        data.assigned_to,
        current_user.id,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Notice not found")

    # Fetch assigned user name
    assigned_user = db.query(User).filter(User.id == data.assigned_to).first()

    assigned_name = assigned_user.full_name if assigned_user else f"User {data.assigned_to}"
    current_name = current_user.full_name 
    # Create timeline entry
    timeline_entry = NoticeTimeline(
        notice_id=notice_id,
        event_type="ASSIGNMENT",
        description=f"Notice assigned to {assigned_name} by {current_name}",
    )

    db.add(timeline_entry)
    db.commit()

    return AssignNoticeResponse(
    message="Notice assigned successfully",
    notice_id=notice_id,
    assigned_to=data.assigned_to
    )


# ---------------------------------------------------------
# 📘 Patch Status (Timeline Logging)
# ---------------------------------------------------------
class UpdateStatusRequest(BaseModel):
    status: str


@router.patch("/{notice_id}/status")
def update_notice_status(
    notice_id: int,
    request: UpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notice = update_notice_status_service(
        db,
        notice_id,
        request.status,
        current_user.id,
    )

    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found.")

    timeline_entry = NoticeTimeline(
        notice_id=notice_id,
        event_type="STATUS_CHANGE",
        description=f"Status changed to {request.status}",
    )

    db.add(timeline_entry)
    db.commit()

    return {"message": "Status updated successfully."}


# ---------------------------------------------------------
# 📘 Get Single Notice
# ---------------------------------------------------------

@router.get("/{notice_id}", response_model=NoticeResponse)
def get_notice_detail(
    notice_id: int,
    db: Session = Depends(get_db),
):
    result = (
        db.query(Notice, NoticeRiskMetadata.risk_score)
        .outerjoin(
            NoticeRiskMetadata,
            NoticeRiskMetadata.notice_id == Notice.id
        )
        .filter(Notice.id == notice_id)
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Notice not found")

    notice, risk_score = result

    # Attach risk score to notice object
    notice.risk_score = float(risk_score) if risk_score else 0

    return notice

    


@router.get("/{notice_id}/timeline")
def get_notice_timeline(
    notice_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    entries = (
        db.query(NoticeTimeline)
        .filter(NoticeTimeline.notice_id == notice_id)
        .order_by(NoticeTimeline.created_at.desc())
        .all()
    )

    return [
        {
            "event_type": e.event_type,
            "description": e.description,
            "created_at": e.created_at
        }
        for e in entries
    ]