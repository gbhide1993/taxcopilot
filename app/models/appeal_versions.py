import uuid
from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base


class AppealVersion(Base):
    __tablename__ = "appeal_versions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    notice_id = Column(
        Integer,
        ForeignKey("notices.id", ondelete="CASCADE"),
        nullable=False
    )

    version_number = Column(Integer, nullable=False)

    background = Column(Text, nullable=False)
    grounds = Column(Text, nullable=False)
    prayer = Column(Text, nullable=False)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False
    )
