from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.draft_service import (generate_structured_draft, 
                                        get_latest_draft,
                                        get_all_draft_versions,
                                        get_all_drafts)
from app.schemas.draft_schema import (DraftResponse,
                                      DraftVersionListResponse)

from fastapi.responses import StreamingResponse
from app.services.export_service import generate_draft_docx
from app.models.draft_version import DraftVersion
from app.models.notice import Notice

router = APIRouter(
    prefix="/draft",
    tags=["Draft"]
)

@router.get("/")
def list_all_drafts(
    db: Session = Depends(get_db)
):
    return get_all_drafts(db)


@router.post("/generate/{notice_id}", response_model=DraftResponse)
def generate_draft(
    notice_id: int,
    db: Session = Depends(get_db)
):
    return generate_structured_draft(db, notice_id)


@router.get("/{notice_id}/latest", response_model=DraftResponse)
def get_latest(
    notice_id: int,
    db: Session = Depends(get_db)
):
    return get_latest_draft(db, notice_id)

@router.get("/{notice_id}/versions")
def get_versions(
    notice_id: int,
    db: Session = Depends(get_db)
):
    versions = get_all_draft_versions(db, notice_id)
    return versions or []

@router.get("/{notice_id}/export/{version_number}")
def export_draft(
    notice_id: int,
    version_number: int,
    db: Session = Depends(get_db)
):
    file_stream = generate_draft_docx(db, notice_id, version_number)

    filename = f"draft_notice_{notice_id}_v{version_number}.docx"

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


   