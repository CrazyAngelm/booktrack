import enum
from sqlalchemy import Column, Integer, String
from core import Base


class ReadingStatus(str, enum.Enum):
    WANT = "Want"
    READING = "Reading"
    READ = "Read"


class ReadingListBook(Base):
    __tablename__ = "reading_list_books"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, nullable=False)
    user_email = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default=ReadingStatus.WANT.value)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)
