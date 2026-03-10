from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse 
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.appeal_service import generate_appeal

from app.schemas.appeal_schema import AppealResponse, AppealVersionListResponse
from app.services.appeal_service import (
    get_latest_appeal,
    get_all_appeal_versions,
    get_all_appeals,
)

from app.services.export_service import generate_appeal_docx

router = APIRouter(prefix="/appeals", tags=["Appeals"])

@router.get("/")
def list_all_appeals(
    db: Session = Depends(get_db)
):
    return get_all_appeals(db)

@router.post("/generate/{notice_id}")
def generate_appeal_endpoint(
    notice_id: int,
    db: Session = Depends(get_db)
):
    appeal = generate_appeal(db, notice_id)

    return {
        "notice_id": appeal.notice_id,
        "version_number": appeal.version_number,
        "background": appeal.background,
        "grounds": appeal.grounds,
        "prayer": appeal.prayer
    }

@router.get("/{notice_id}/latest", response_model=AppealResponse)
def get_latest_appeal_endpoint(
    notice_id: int,
    db: Session = Depends(get_db)
):
    return get_latest_appeal(db, notice_id)


@router.get("/{notice_id}/versions", response_model=AppealVersionListResponse)
def get_all_versions_endpoint(
    notice_id: int,
    db: Session = Depends(get_db)
):
    appeals = get_all_appeal_versions(db, notice_id)

    return {
        "notice_id": notice_id,
        "versions": appeals
    }

@router.get("/{notice_id}/export/{version_number}")
def export_appeal(
    notice_id: int,
    version_number: int,
    db: Session = Depends(get_db)
):
    file_stream = generate_appeal_docx(db, notice_id, version_number)

    filename = f"appeal_notice_{notice_id}_v{version_number}.docx"

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
