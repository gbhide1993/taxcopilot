from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import text
from app.database import Base


class NoticeAssignment(Base):
    __tablename__ = "notice_assignments"

    id = Column(Integer, primary_key=True, index=True)

    notice_id = Column(
        Integer,
        ForeignKey("notices.id", ondelete="CASCADE"),
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    role = Column(String, nullable=False)

    assigned_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
