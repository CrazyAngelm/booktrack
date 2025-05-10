from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
)
from core.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    page = Column(Integer, primary_key=True, index=True)
    fetched_at = Column(
        DateTime, default=datetime.now, nullable=False
    )

    title = Column(String, nullable=False)
    subjects = Column(JSON, nullable=False)
    authors = Column(JSON, nullable=False)
    summaries = Column(JSON, nullable=False)
    translators = Column(JSON, nullable=False)
    languages = Column(JSON, nullable=False)
    copyright = Column(Boolean, nullable=True)
    media_type = Column(String, nullable=False)
    formats = Column(JSON, nullable=False)
    download_count = Column(Integer, nullable=False)
