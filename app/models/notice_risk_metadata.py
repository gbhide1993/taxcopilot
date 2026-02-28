from sqlalchemy import Column, Integer, Boolean, Float, TIMESTAMP, ForeignKey
from sqlalchemy.sql import text
from app.database import Base


class NoticeRiskMetadata(Base):
    __tablename__ = "notice_risk_metadata"

    notice_id = Column(
        Integer,
        ForeignKey("notices.id", ondelete="CASCADE"),
        primary_key=True
    )

    severity_score = Column(Integer, nullable=False)
    days_remaining = Column(Integer, nullable=False)
    repeat_flag = Column(Boolean, nullable=False, default=False)
    risk_score = Column(Float, nullable=False)

    last_updated = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
