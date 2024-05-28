from datetime import datetime
from pydantic import BaseModel

__all__ = ["Person", "Paper", "Session"]


class Person(BaseModel):
    name: str
    organization: str
    country: str | None = None
    email: str | None = None


class Paper(BaseModel):
    id: int
    title: str
    order: int
    contact: Person
    pages: tuple[int, int] | None
    abstract: str
    keywords: list[str]
    authors: list[Person]
    start_time: datetime | None = None
    plenary: bool = False


class Session(BaseModel):
    name: str
    type: str
    code: str
    category: tuple[str, int | None]
    category_order: int | None
    location: str
    chairs: list[Person]
    start_time: datetime
    end_time: datetime
    papers: list[Paper] = []
