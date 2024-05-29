"""Fundamental classes for the NOLTA Symposium Publication Tools.


.. _国際会議メタデータ仕様書: https://www.ieice.org/jpn/books/pdf/metadata.pdf

"""

from typing import Generic, Literal, TypeAlias, TypeVar
from datetime import date, datetime, time
import json

import re
from pydantic import BaseModel

T = TypeVar("T")
Comment: TypeAlias = Literal["", "#"]

__all__ = [
    "MetaPerson",
    "MetaSession",
    "MetaPaper",
    "MetaCommon",
    "Metadata",
    "Award",
    "CommonInfo",
    "ReviseItem",
]


class Award(BaseModel):
    """Award information to load from the JSON file.

    Parameters
    ----------
    id : str
        Award ID.
    awards : list[str]
        Awards received.

    Examples
    --------
    With the following JSON file:

    .. code-block:: json

        [
            {
                "id": "1",
                "awards": ["Best Paper Award"]
            },
            {
                "id": "2",
                "awards": ["Best Paper Award", "Best Presentation Award"]
            }
        ]

    The following code:

    .. code-block:: python

        with open("awards.json", "r") as f:
            a_data = [Award(**a) for a in json.load(f)]

    will create a list of :class:`Award` instances.

    Note
    ----
    IEICE における 国際会議メタデータ仕様書_


    """

    id: str
    awards: list[str]


class CommonInfo(BaseModel):
    """Common information to load from the JSON file.

    Parameters
    ----------
    conf_abbr : str
        Conference abbreviation.
    year : int
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
        Cooperators. （主催／共催／協賛／後援）
    publication : str
        Publication.
    date_published : date
        Date published.
    publisher : str
        Publisher.

    Examples
    --------
    With the following JSON file:

    .. code-block:: json

        {
            "conf_abbr": "NOLTA",
            "year": 2024,
            "event_name": "NOLTA 2024",
            "event_date": ["2024-11-20", "2024-11-22"],
            "event_city": ["Tokyo"],
            "event_venue": ["Tokyo International Forum"],
            "event_web_url": "https://www.nolta2024.org",
            "cooperators": [
                ["IEICE"],
                ["IEEE", "RISP"],
                [],
                []
            ],
            "publication": "Proceedings of NOLTA 2024",
            "date_published": "2024-11-20",
            "publisher": "IEICE"
        }

    The following code:

    .. code-block:: python

        with open("common.json", "r") as f:
            data = CommonInfo(**json.load(f))

    will create an instance of :class:`CommonInfo`.

    Note
    ----
    IEICE における 国際会議メタデータ仕様書_


    """

    conf_abbr: str
    year: int
    event_name: str
    event_date: tuple[date, date]
    event_city: list[str]
    event_venue: list[str]
    event_web_url: str
    cooperators: tuple[list[str], list[str], list[str], list[str]]
    publication: str
    date_published: date
    publisher: str


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


    Note
    ----
    IEICE における 国際会議メタデータ仕様書_


    See Also
    --------
    MetaSession
    MetaPaper

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


class Metadata:
    def as_list(self) -> list[str]:
        return [str(a) for a in self.__dict__.values()]


class MetaSession(Metadata):
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


class MetaPaper(Metadata):
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


class MetaCommon(Metadata):
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


class ReviseItem(BaseModel):
    """Item to be revised.

    Parameters
    ----------
    pdfname : str
        PDF file name.
    errors : list[str]
        List of errors.
    ext_msg : str | None
        Extra message.
    paper_id : int
        Paper ID.
    title : str
        Title.
    contact : Person
        Contact information of the corresponding author.
    """

    pdfname: str
    errors: list[str]
    ext_msg: str | None
    paper_id: int
    title: str
    contact: Person


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(obj.__class__, BaseModel):
            return dict(obj)
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        return super().default(obj)


class SMTPConfig:
    def __init__(
        self,
        SMTP_SERVER: str,
        SMTP_PORT: int,
        SMTP_USER: str,
        SMTP_USERNAME: str,
        SMTP_PASSWORD: str | None = None,
    ) -> None:
        self.SMTP_SERVER = SMTP_SERVER
        self.SMTP_PORT = SMTP_PORT
        self.SMTP_USER = SMTP_USER
        self.SMTP_USERNAME = SMTP_USERNAME
        self.SMTP_PASSWORD = SMTP_PASSWORD


class SSOrganizer(BaseModel):
    category: tuple
    title: str
    organizers: list[Person]
