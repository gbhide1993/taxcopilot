from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import text
from app.database import Base


class NoticeTimeline(Base):
    __tablename__ = "notice_timeline"

    id = Column(Integer, primary_key=True, index=True)

    notice_id = Column(
        Integer,
        ForeignKey("notices.id", ondelete="CASCADE"),
        nullable=False
    )

    event_type = Column(String, nullable=False)

    description = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
