from typing import Any

from pydantic import BaseModel, ConfigDict

class FavouriteBase(BaseModel):
    book_id: int
    user_email: str
    def __init__(self, **data: Any):
        super().__init__(**data)


class FavouriteCreate(FavouriteBase):
    pass

class FavouriteUpdate(FavouriteBase):
    pass

class FavouriteRead(FavouriteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)