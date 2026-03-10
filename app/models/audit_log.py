from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_name = Column(String, nullable=False)

    action = Column(String, nullable=False)          # e.g., CREATE_CLIENT
    entity_type = Column(String, nullable=False)     # e.g., Client
    entity_id = Column(Integer, nullable=True)

    details = Column(JSON, nullable=True)            # optional metadata

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
