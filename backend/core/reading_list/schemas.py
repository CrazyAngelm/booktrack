from typing import Any
import datetime
from pydantic import BaseModel, ConfigDict


class ReadingListBookBase(BaseModel):
    book_id: int
    user_email: str
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    
    def __init__(self, **data: Any):
        super().__init__(**data)


class ReadingListBookCreate(ReadingListBookBase):
    pass


class ReadingListBookUpdate(ReadingListBookBase):
    pass


class ReadingListBookRead(ReadingListBookBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
