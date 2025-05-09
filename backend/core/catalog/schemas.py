from typing import Any

from pydantic import BaseModel, ConfigDict


class Person(BaseModel):
    name: str
    birth_year: int | None = None
    death_year: int | None = None
    
    def __init__(self, **data: Any):
        super().__init__(**data)


class BookBase(BaseModel):
    title: str
    subjects: list[str]
    authors: list[Person]
    summaries: list[str]
    translators: list[Person]
    languages: list[str]
    copyright: bool | None = None
    media_type: str
    formats: dict[str, str]
    download_count: int
    
    def __init__(self, **data: Any):
        super().__init__(**data)


class BookCreate(BookBase):
    pass


class BookRead(BookBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
