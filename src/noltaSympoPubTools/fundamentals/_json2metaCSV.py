from typing import Generic, Literal, TypeAlias, TypeVar
from datetime import date

import re
from pydantic import BaseModel

T = TypeVar("T")
Comment: TypeAlias = Literal["", "#"]

__all__ = [
    "MetaPerson",
    "MetaSession",
    "MetaPaper",
    "MetaCommon",
    "AsList",
    "Award",
    "CommonInfo",
]


class Award(BaseModel):
    """Award information to load from the JSON file."""

    id: str
    """Award ID."""
    awards: list[str]
    """Awards received."""


class CommonInfo(BaseModel):
    """Common information to load from the JSON file."""

    conf_abbr: str
    """Conference abbreviation."""
    year: int
    """Year."""
    event_name: str
    """Event name."""
    event_date: tuple[date, date]
    """Event date."""
    event_city: list[str]
    """Event city."""
    event_venue: list[str]
    """Event venue."""
    event_web_url: str
    """Event website URL."""
    cooperators: tuple[list[str], list[str], list[str], list[str]]
    """Cooperators."""
    publication: str
    """Publication."""
    date_published: date
    """Date published."""
    publisher: str
    """Publisher."""


class Str(str):
    def __init__(self, value: str) -> None:
        if len(value) > 1000:
            raise ValueError(f"String too long (up to 1000): {value}")

        # Raise error if value contains newline
        if re.search(r"\n", value) is not None:
            raise ValueError(f"String contains newline: {value}")

        self.value = value


class Strs:
    def __init__(self, strs: list[Str]) -> None:
        if len(strs) > 100:
            strs = strs[:100]
        self.strs = strs

    def __str__(self) -> str:
        return ";".join([str(s) for s in self.strs])


class Url(str):
    def __init__(self, value: str) -> None:
        if not (value.startswith("http://") or value.startswith("https://")):
            raise ValueError(f"Invalid URL: {value}")

        self.value = value


class MetaPerson:
    """Person information in the context of the Metadata CSV.

    Parameters
    ----------
    fullname : str
        Full name.
    """

    def __init__(self, fullname: str) -> None:
        self.fullname = fullname.split()
        self.fullname.reverse()

    def __str__(self) -> str:
        return " ".join(self.fullname)


class SlashList(Generic[T]):
    def __init__(self, list: list[T]) -> None:
        self.list = list

    def __str__(self) -> str:
        return "/".join([str(item) for item in self.list])


class AtList(Generic[T]):
    def __init__(self, list: list[T]) -> None:
        self.list = list

    def __str__(self) -> str:
        return "@@".join([str(item) for item in self.list])


class Date:
    def __init__(self, date: date) -> None:
        self.date = date

    def __str__(self) -> str:
        return self.date.strftime("%Y-%m-%d")


class Id:
    def __init__(self, number: str) -> None:
        if re.match(r"^[A-Za-z0-9\-./]{1,100}$", number) is None:
            raise ValueError(f"Invalid session number: {number}")
        self.number = number

    def __str__(self) -> str:
        return self.number


class AsList:
    def as_list(self) -> list[str]:
        return [str(a) for a in self.__dict__.values()]


class MetaSession(AsList):
    """Session information in the context of the Metadata CSV.

    Parameters
    ----------
    comment : Comment
        Comment.
    number : str
        Session number.
    name : str
        Session name.
    date : date
        Session date.
    organizers : list[str]
        Organizers.
    org_affils : list[str]
        Organizers' affiliations.
    chairs : list[str]
        Chairs.
    chair_affils : list[str]
        Chairs' affiliations.
    cities : list[str]
        Cities.
    venues : list[str]
        Venues.
    """

    def __init__(
        self,
        comment: Comment,
        number: str,
        name: str,
        date: date,
        organizers: list[str],
        org_affils: list[str],
        chairs: list[str],
        chair_affils: list[str],
        cities: list[str],
        venues: list[str],
    ) -> None:
        self.comment = comment  # 1
        self.number = Id(number)  # 2
        self.name = Str(name)  # 3
        self.date = Date(date)  # 4
        self.organizers: AtList[MetaPerson] = AtList(
            [MetaPerson(o) for o in organizers]
        )  # 5
        self.org_affils: AtList[Str] = AtList([Str(a) for a in org_affils])  # 6
        self.chairs: AtList[MetaPerson] = AtList([MetaPerson(c) for c in chairs])  # 7
        self.chair_affils: AtList[Str] = AtList([Str(ca) for ca in chair_affils])  # 8
        self.cities = Strs([Str(c) for c in cities])  # 9
        self.venues = Strs([Str(v) for v in venues])  # 10


class Text:
    def __init__(self, text: str) -> None:
        if len(text) > 10000:
            raise ValueError(f"String too long (up to 1000): {text}")

        # Replace newline with HTML tag <br>
        text = text.replace("\n", "<br>")

        self.text = text

    def __str__(self) -> str:
        return self.text


class MetaPaper(AsList):
    """Paper information in the context of the Metadata CSV.

    Parameters
    ----------
    comment : Comment
        Comment.
    title : str
        Title.
    filename : str
        Filename.
    abstract : str
        Abstract.
    keywords : list[str]
        Keywords.
    pages : tuple[int, int] | None
        Pages, or None if not available.
    session : str
        Session ID.
    number : str
        Paper number.
    awards : list[str]
        Awards received.
    authors : list[str]
        Authors.
    affils : list[str]
        Affiliations of authors.
    """

    def __init__(
        self,
        comment: Comment,
        title: str,
        filename: str,
        abstract: str,
        keywords: list[str],
        pages: tuple[int, int] | None,
        session: str,
        number: str,
        awards: list[str],
        authors: list[str],
        affils: list[str],
    ) -> None:
        self.comment = comment  # 1
        self.title = Str(title)  # 2
        self.filename = Str(filename)  # 3
        self.abstract = Text(abstract)  # 4
        self.keywords = Strs([Str(k) for k in keywords])  # 5
        if pages is None:
            self.page_from = ""
            self.page_to = ""
        else:
            self.page_from = pages[0]  # 6
            self.page_to = pages[1]  # 7
        self.session = Id(session)  # 8
        self.volume = ""  # 9
        self.number = Id(number)  # 10
        self.awards = Strs([Str(a) for a in awards])  # 11
        self.authors: AtList[MetaPerson] = AtList(
            [MetaPerson(a) for a in authors]
        )  # 12
        self.affils: AtList[Str] = AtList([Str(a) for a in affils])  # 13


class MetaCommon(AsList):
    """Common information in the context of the Metadata CSV.

    Parameters
    ----------
    comment : Comment
        Comment.
    conf_abbr : str
        Conference name abbreviation.
    year : str
        Year.
    event_name : str
        Event name.
    event_date : tuple[date, date]
        Event date.
    event_city : list[str]
        Event city.
    event_venue : list[str]
        Event venue.
    event_web_url : str
        Event website URL.
    cooperators : tuple[list[str], list[str], list[str], list[str]]
        Cooperators.
    publication : str
        Publication.
    date_published : date
        Date published.
    publisher : str
        Publisher.
    """

    def __init__(
        self,
        comment: Comment,
        conf_abbr: str,
        year: str,
        event_name: str,
        event_date: tuple[date, date],
        event_city: list[str],
        event_venue: list[str],
        event_web_url: str,
        cooperators: tuple[list[str], list[str], list[str], list[str]],
        publication: str,
        date_published: date,
        publisher: str,
    ) -> None:
        self.comment = comment  # 1
        self.conf_name = ""  # 2
        self.conf_abbr = Str(conf_abbr)  # 3
        self.year = Str(year)  # 4
        self.body_url = ""  # 5
        self.event_name = Str(event_name)  # 6
        self.event_date_from = Date(event_date[0])  # 7
        self.event_date_to = Date(event_date[1])  # 8
        self.event_city = Strs([Str(c) for c in event_city])  # 9
        self.event_venue = Strs([Str(v) for v in event_venue])  # 10
        self.event_web_url = Url(event_web_url)  # 11
        self.cooperators: SlashList[Strs] = SlashList(
            [Strs([Str(c) for c in co]) for co in cooperators]
        )  # 12
        self.publication = Str(publication)  # 13
        self.date_published = Date(date_published)  # 14
        self.copyright_holder = ""  # 15
        self.publisher = Str(publisher)  # 16
