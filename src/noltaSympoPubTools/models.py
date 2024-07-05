"""Fundamental classes for the NOLTA Symposium Publication Tools.


.. _国際会議メタデータ仕様書: https://www.ieice.org/jpn/books/pdf/metadata.pdf

"""

from typing import Generic, Literal, TypeAlias, TypeVar
from datetime import date, datetime, time
import json
import csv

import re
from pydantic import BaseModel

T = TypeVar("T")
TBM = TypeVar("TBM", bound=BaseModel)
Comment: TypeAlias = Literal["", "#"]

__all__ = [
    "MetaPerson",
    "MetaSession",
    "MetaSessionList",
    "MetaArticle",
    "MetaArticleList",
    "MetaCommon",
    "Metadata",
    "MetadataList",
    "Award",
    "AwardList",
    "CommonInfo",
    "ReviseItem",
    "ReviseItemList",
    "BaseModelList",
    "Session",
    "SessionList",
    "SSOrganizer",
    "SSOrganizerList",
    "Person",
    "Paper",
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
    In the JSON format, the data should be structured as follows:

    .. literalinclude:: /py_examples/awards.json
        :caption: awards.json
        :language: json

    Note
    ----
    IEICE における 国際会議メタデータ仕様書_

    See Also
    --------
    .AwardList: List of awards
    .load_meta_articles: Load award information from JSON file
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
    In the JSON format, the data should be structured as follows:

    .. literalinclude:: /py_examples/common.json
        :caption: common.json
        :language: json

    Note
    ----
    IEICE における 国際会議メタデータ仕様書_

    See Also
    --------
    .MetaCommon: Data class for common information
    .load_meta_common: Load common information from JSON file

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
    .MetaSession
    .MetaArticle

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
    """Base class for metadata."""

    def as_list(self) -> list[str]:
        return [str(a) for a in self.__dict__.values()]

    def dump_csv(self, filename: str, template: str) -> None:
        """Save metadata as CSV file.

        Parameters
        ----------
        filename : str
            Output CSV file path.
        template : str
            Template CSV file path. The template file should have the same structure as the output CSV file.
            Required fields are dependent on the metadata type, but the first two rows should be the headers.

        See Also
        --------
        .MetaCommon: Data class for common information
        .load_meta_common: Load common information from JSON file
        """
        _dump_metadata_csv(self, filename, template)


TMD = TypeVar("TMD", bound=Metadata)


class MetadataList(list[TMD], Generic[TMD]):
    """List of metadata."""

    def dump_csv(self, filename: str, template: str) -> None:
        """Save metadata as CSV file.

        Parameters
        ----------
        filename : str
            Output CSV file path.
        template : str
            Template CSV file path. The template file should have the same structure as the output CSV file.
            Required fields are dependent on the metadata type, but the first two rows should be the headers.

        See Also
        --------
        .MetaSessionList: List of session information
        .MetaArticleList: List of paper information
        .load_meta_sessions: Load session information from JSON file
        .load_meta_articles: Load paper information from JSON file
        """
        _dump_metadata_csv(self, filename, template)


def _dump_metadata_csv(
    obj: Metadata | MetadataList, filename: str, template: str
) -> None:
    try:
        with open(template, "r") as f:
            reader = csv.reader(f)
            headers = [next(reader), next(reader)]
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found: {template}")

    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers[0])
        writer.writerow(headers[1])
        if isinstance(obj, Metadata):
            writer.writerow(obj.as_list())
        else:
            for d in obj:
                writer.writerow(d.as_list())


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

    See Also
    --------
    .MetaSessionList : List of session information
    .load_meta_sessions : Load session information from JSON file
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


class MetaArticle(Metadata):
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

    See Also
    --------
    .MetaArticleList : List of paper information
    .load_meta_articles : Load paper information from JSON file
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


class MetaSessionList(MetadataList[MetaSession]):
    """List of session information in the context of the Metadata CSV.

    Parameters
    ----------
    sessions : list[dict]
        List of session dictionaries. Each dictionary should have the structure of :class:`.MetaSession`.
        Generally, the data will be loaded from a JSON file.

    See Also
    --------
    .load_meta_sessions: Load session information from JSON file
    .MetaSession: Data class for session
    """

    def __init__(self, sessions: list[dict] = []) -> None:
        super().__init__([MetaSession(**s) for s in sessions])


class MetaArticleList(MetadataList[MetaArticle]):
    """List of paper information in the context of the Metadata CSV.

    Parameters
    ----------
    articles : list[dict]
        List of paper dictionaries. Each dictionary should have the structure of :class:`.MetaArticle`.
        Generally, the data will be loaded from a JSON file.

    See Also
    --------
    .load_meta_articles: Load paper information from JSON file
    .MetaArticle: Data class for paper
    """

    def __init__(self, articles: list[dict] = []) -> None:
        super().__init__([MetaArticle(**a) for a in articles])


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

    See Also
    --------
    .load_meta_common: Load common information from JSON file
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
    """Person information.

    Parameters
    ----------
    name : str
        Name.
    organization : str
        Organization.
    country : str | None
        Country.
    email : str | None
        Email.

    See Also
    --------
    .Paper: Data class for paper
    .Session: Data class for session
    .load_epapers_sheet: Convert CSV to JSON
    """

    name: str
    organization: str
    country: str | None = None
    email: str | None = None


class Paper(BaseModel):
    """Paper information.

    Parameters
    ----------
    id : int
        Paper ID.
    title : str
        Title.
    order : int
        Order.
    contact : Person
        Contact information of the corresponding author.
    pages : tuple[int, int] | None
        Pages, or None if not available.
    abstract : str
        Abstract.
    keywords : list[str]
        Keywords.
    authors : list[Person]
        List of authors.
    start_time : datetime | None
        Start time.
    plenary : bool
        Plenary session or not.

    See Also
    --------
    .Person: Data class for person
    .Session: Data class for session
    .load_epapers_sheet: Convert CSV to JSON
    """

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
    """Session information.

    Parameters
    ----------
    name : str
        Session name.
    type : str
        Session type.
    code : str
        Session code.
    category : tuple[str, int | None]
        Category information.
    category_order : int | None
        Category order.
    location : str
        Location.
    chairs : list[Person]
        List of chairs.
    start_time : datetime
        Start time.
    end_time : datetime
        End time.
    papers : list[Paper]
        List of papers.

    See Also
    --------
    .Person: Data class for person
    .Paper: Data class for paper
    .load_epapers_sheet: Convert CSV to JSON
    .SessionList: List of sessions
    """

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


class BaseModelList(list[TBM], Generic[TBM]):
    """List of basemodels.

    Parameters
    ----------
    self : list[object]
        List of BaseModel objects.

    See Also
    --------
    .AwardList: List of awards
    .ReviseItemList: List of revise items
    .SessionList: List of sessions
    .SSOrganizerList: List of session organizers
    """

    def dump_json(self, filename: str, verbose: bool = False, **kwargs) -> None:
        """Save data to JSON file.

        Parameters
        ----------
        filename : str
            Output JSON filename.
        verbose : bool, optional
            Print detail, by default False.
        kwargs : Any
            Additional keyword arguments for :func:`json.dump`.
        """
        kwargs = {
            "indent": 4,
            "cls": JsonEncoder,
            "ensure_ascii": False,
        } | kwargs
        json.dump(obj=self, fp=open(filename, "w"), **kwargs)
        if verbose:
            print("dump_json: Data counts:", len(self))
            print("dump_json: Output filename:", filename)
            print("dump_json: Data type:", type(self[0]))


class SessionList(BaseModelList[Session]):
    """List of sessions.

    Parameters
    ----------
    sessions : list[dict]
        List of session dictionaries. Each dictionary should have the structure of :class:`.Session`.
        Generally, the data will be loaded from a JSON file.

    See Also
    --------
    .Session: Data class for session
    .BaseModelList: List of basemodels
    """

    def __init__(self, sessions: list[dict] = []) -> None:
        super().__init__([Session(**s) for s in sessions])


class ReviseItem(BaseModel):
    """Item to be revised.

    Parameters
    ----------
    pdf_name : str
        PDF file name.
    errors : list[str]
        List of errors.
    extra_comments : str | None
        Extra message.
    id : int
        Paper ID.
    title : str
        Title.
    contact : Person
        Contact information of the corresponding author.

    See Also
    --------
    .Person: Data class for person
    .ReviseItemList: List of revise items
    .handleEmail: Module for handling emails
    """

    pdf_name: str
    errors: list[str]
    id: int
    title: str
    contact: Person
    extra_comments: str | None = None


class AwardList(BaseModelList[Award]):
    """List of awards.

    Parameters
    ----------
    awards : list[dict]
        List of award dictionaries. Each dictionary should have the structure of :class:`.Award`.
        Generally, the data will be loaded from a JSON file.

    See Also
    --------
    .Award: Data class for award
    .BaseModelList: List of basemodels
    .load_meta_articles: Load award information from JSON file
    """

    def __init__(self, awards: list[dict] = []) -> None:
        super().__init__([Award(**a) for a in awards])


class ReviseItemList(BaseModelList[ReviseItem]):
    """List of :class:`.ReviseItem`.

    Parameters
    ----------
    revise_items : list[dict]
        List of revise item dictionaries. Each dictionary should have the structure of :class:`.ReviseItem`.
        Generally, the data will be loaded from a JSON file.

    See Also
    --------
    .ReviseItem: Data class for revise item
    .handleEmail: Module for handling emails
    """

    def __init__(self, revise_items: list[dict] = []) -> None:
        self._revise_items = [ReviseItem(**r) for r in revise_items]
        super().__init__(self._revise_items)


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
    """Session organizer information.

    Parameters
    ----------
    category : tuple
        Category information.
    title : str
        Session title.
    organizers : list[Person]
        List of organizers.

    Examples
    --------
    In the JSON format, the data should be structured as follows:

    .. literalinclude:: /py_examples/ss_organizers.json
        :caption: ss_organizers.json
        :language: json

    See Also
    --------
    .SSOrganizerList: List of session organizers
    """

    category: tuple
    title: str
    organizers: list[Person]


class SSOrganizerList(BaseModelList[SSOrganizer]):
    """List of session organizers.

    Parameters
    ----------
    ss_organizers : list[dict]
        List of session organizer dictionaries. Each dictionary should have the structure of :class:`.SSOrganizer`.
        Generally, the data will be loaded from a JSON file.

    See Also
    --------
    .SSOrganizer: Data class for session
    .load_meta_sessions: Load session information from JSON file
    """

    def __init__(self, ss_organizers: list[dict] = []) -> None:
        super().__init__([SSOrganizer(**s) for s in ss_organizers])
