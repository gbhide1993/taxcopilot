from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.database import get_db
from app.services.report_export_service import export_reports

router = APIRouter(
    prefix="/reports/export",
    tags=["Reports"]
)


@router.get("/")
def export_report(
    type: str = Query(...),
    db: Session = Depends(get_db)
):

    file_stream = export_reports(db, type)

    filename = f"{type}_report.csv"

    return StreamingResponse(
        file_stream,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )