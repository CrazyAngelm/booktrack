from sqlalchemy import Column, Integer, String


from core import Base


class Favourite(Base):
    __tablename__ = "favourites"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, nullable=False)
    user_email = Column(String(255), nullable=False)