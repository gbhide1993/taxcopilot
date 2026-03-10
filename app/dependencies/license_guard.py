from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.license import License


def check_license(db: Session = Depends(get_db)):
    license = db.query(License).first()

    if not license:
        raise HTTPException(status_code=403, detail="License not configured")

    today = date.today()

    # Expired
    if not license.is_active or today > license.expiry_date:
        raise HTTPException(
            status_code=403,
            detail="License expired. Please renew to continue using the system."
        )
