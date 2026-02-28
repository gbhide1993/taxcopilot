from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.notice import Notice
from app.models.user import User
from app.models.notice_assignment import NoticeAssignment

def assign_notice(db: Session, notice_id: int, assigned_to: int, role: str):

    notice = db.query(Notice).filter(Notice.id == notice_id).first()

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notice not found."
        )

    user = db.query(User).filter(User.id == assigned_to).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    # Insert into assignment history
    assignment = NoticeAssignment(
        notice_id=notice_id,
        assigned_to=assigned_to,
        role=role
    )

    db.add(assignment)

    # Update current assignment on notice table
    notice.assigned_to = assigned_to

    db.commit()

    return {
        "notice_id": notice_id,
        "assigned_to": assigned_to,
        "role": role,
        "message": "Notice assigned successfully."
    }
