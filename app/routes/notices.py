import os
import fitz
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from app.services.notice_service import classify_notice
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.role_guard import require_role
from app.schemas.notice_schema import (NoticeCreate, NoticeUpdateStatus, NoticeAssign, NoticeResponse)
from app.services.notice_service import (create_notice, list_notices, update_notice_status, assign_notice, classify_notice)
from app.models.notice import NoticeStatus, Notice
from app.services.notice_parser_service import (extract_section, extract_assessment_year, extract_dates)
from datetime import date, timedelta
from app.dependencies.license_guard import check_license
from app.schemas.assignment_schema import (AssignNoticeRequest, AssignNoticeResponse)
from app.services.assignment_service import assign_notice
from app.models.notice_timeline import NoticeTimeline
from pydantic import BaseModel
from app.services.notice_service import update_notice_status as update_notice_status_service
from app.models.user import User

class UpdateStatusRequest(BaseModel):
    status: str

router = APIRouter(prefix="/notices", tags=["Notices"])


@router.post("/", response_model=NoticeResponse)
def create_new_notice(
    notice: NoticeCreate,
    db: Session = Depends(get_db),
    firm=Depends(check_license),
    current_user = Depends(get_current_user)
):
    # 1️⃣ Classify notice text
    classification = classify_notice(notice.description or "")

    # 2️⃣ Create notice using classification
    return create_notice(
        db=db,
        notice_data=notice,
        created_by=current_user.id
        
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
    current_user=Depends(require_role(["ADMIN", "SENIOR_CA"]))
):
    try:
        # 1️⃣ Read PDF
        contents = file.file.read()
        pdf = fitz.open(stream=contents, filetype="pdf")

        extracted_text = ""
        for page in pdf:
            extracted_text += page.get_text()

        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="Unable to extract text from PDF.")

        # 2️⃣ Extract structured fields
        section_reference = extract_section(extracted_text)
        assessment_year = extract_assessment_year(extracted_text)
        received_date, due_date = extract_dates(extracted_text)

        # 3️⃣ Fallback logic if dates not detected
        if not received_date:
            received_date = date.today()

        if not due_date:
            due_date = received_date + timedelta(days=30)

        # 4️⃣ Create Notice entry
        notice = Notice(
            notice_number=file.filename,
            notice_type="Income Tax Notice",
            section_reference=section_reference,
            assessment_year=assessment_year,
            description="Auto-classified notice",
            received_date=received_date,
            due_date=due_date,
            status="open",
            client_id=client_id,
            created_by=current_user.id,
            assigned_to=None,
            raw_text=extracted_text
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
            "due_date": str(due_date)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_notices(
    status: NoticeStatus = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return list_notices(
        db=db,
        user_id=current_user.id,
        status=status,
        page=page,
        page_size=page_size,
    )

@router.put("/{notice_id}/status", response_model=NoticeResponse)
def change_status(
    notice_id: int,
    data: NoticeUpdateStatus,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated = update_notice_status(db, notice_id, data.status, current_user.id)

    if not updated:
        raise HTTPException(status_code=404, detail="Notice not found")

    return updated


@router.put("/{notice_id}/assign", response_model=NoticeResponse)
def assign(
    notice_id: int,
    data: NoticeAssign,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated = assign_notice(db, notice_id, data.assigned_to, current_user.id)

    if not updated:
        raise HTTPException(status_code=404, detail="Notice not found")

    return updated


@router.post("/{notice_id}/assign", response_model=AssignNoticeResponse)
def assign_notice_endpoint(
    notice_id: int,
    request: AssignNoticeRequest,
    db: Session = Depends(get_db)
):
    return assign_notice(
        db,
        notice_id,
        request.assigned_to,
        request.role
    )

@router.patch("/{notice_id}/status")
def update_notice_status(
    notice_id: int,
    request: UpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notice = update_notice_status_service(
        db,
        notice_id,
        request.status,
        current_user.id
    )

    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found.")

    # Insert timeline record AFTER service update
    timeline_entry = NoticeTimeline(
        notice_id=notice_id,
        event_type="STATUS_CHANGE",
        description=f"Status changed to {request.status}"
    )

    db.add(timeline_entry)
    db.commit()

    return {"message": "Status updated successfully."}

@router.get("/{notice_id}")
def get_notice_detail(
    notice_id: int,
    db: Session = Depends(get_db)
):
    notice = db.query(Notice).filter(Notice.id == notice_id).first()

    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")

    return notice