from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from app.database import Base


class DraftVersion(Base):
    __tablename__ = "draft_versions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    notice_id = Column(
        Integer,
        ForeignKey("notices.id", ondelete="CASCADE"),
        nullable=False
    )

    version_number = Column(Integer, nullable=False)

    introduction = Column(Text, nullable=False)
    facts_summary = Column(Text, nullable=False)
    legal_position = Column(Text, nullable=False)
    section_reference = Column(Text, nullable=False)
    prayer = Column(Text, nullable=False)

    created_at = Column(
        TIMESTAMP,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )
