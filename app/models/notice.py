from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Text, Index
from sqlalchemy.orm import relationship
from app.database import Base
import enum



class NoticeStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    replied = "replied"
    closed = "closed"


class Notice(Base):
    __tablename__ = "notices"
    
    id = Column(Integer, primary_key=True, index=True)

    notice_number = Column(String, nullable=False)
    notice_type = Column(String, nullable=False)

    act_name = Column(String, nullable=True)
    section_reference = Column(String, nullable=True)
    
    assessment_year = Column(String, nullable=True)
    description = Column(String, nullable=True)

    received_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    status = Column(Enum(NoticeStatus), default=NoticeStatus.open)

    client_id = Column(Integer, ForeignKey("clients.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    client = relationship("Client")

    raw_text = Column(Text, nullable=True)

# Composite index for dashboard queries
Index("idx_notice_dashboard", Notice.status, Notice.due_date)
