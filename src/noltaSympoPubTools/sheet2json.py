from collections.abc import Callable
from string import ascii_uppercase
import numpy as np
import json
from datetime import datetime, timedelta, timezone
from pandas import DataFrame, read_excel, read_csv

from .models import Session, Paper, Person, SessionList

__all__ = [
    "load_epapers_sheet",
    "default_session_sort_func",
    "update_sessions",
]


def default_session_sort_func(s: Session) -> int:
    """Default sort function for sessions. Sort by category and category_order. This function is compatible with the ``sort`` method of the list.

    Parameters
    ----------
    s : Session
        Session object.

    Returns
    -------
    int
        Sort key.
    """
    code = s.code.replace("L-", "")
    for index, letter in enumerate(ascii_uppercase, start=1):
        code = code.replace(letter, str(index))
    return int(code)


def _update_papers(session: Session, papers: list[dict]):
    for p in papers:
        for idx_p, p_s in enumerate(session.papers):
            if p_s.id == p["id"]:
                session.papers[idx_p] = p_s.model_copy(update=p)
                break


def update_sessions(
    data_json: str, update_json: str, overwrite: bool = False
) -> SessionList:
    """Update session data with the update data.
    This method is useful when you need to update the session data with the latest information.

    Parameters
    ----------
    data_json : str
        Input JSON filename.
    update_json : str
        Update JSON filename. The fields ``category`` and ``category_order`` are necessary to identify the session.
        If updating papers, the field ``papers`` is also necessary.
        For each updating paper, the field ``id`` is necessary to identify the paper.
    overwrite : bool, optional
        Overwrite the input JSON file, by default False.

    Examples
    --------
    We have the following JSON files:

    .. literalinclude:: ../py_examples/data.json
        :caption: data.json
        :language: json

    .. literalinclude:: ../py_examples/update.json
        :caption: update.json
        :language: json

    Here is an example of how to update the session data with the update data.

    .. literalinclude:: ../py_examples/ex_update_sessions.py

    .. literalinclude:: ../py_examples/update.diff
        :caption: diff between ``data.json`` and ``updated_data.json``

    """
    with open(data_json) as f:
        sessions = SessionList(json.load(f))

    with open(update_json) as f:
        update_dict = json.load(f)

    # categories = [(s.category, s.category_order) for s in sessions]

    # Search for BaseModel Update
    for ud in update_dict:
        for idx, s in enumerate(sessions):
            if (
                s.category[0] == ud["category"][0]
                and s.category[1] == ud["category"][1]
                and s.category_order == ud["category_order"]
            ):
                papers = ud.pop("papers")
                update_session = s.model_copy(update=ud)
                _update_papers(update_session, papers)
                sessions[idx] = update_session
                break
            else:
                if idx == len(sessions) - 1:
                    raise ValueError(
                        f"Session not found: {ud['category']} {ud['category_order']} ({update_json} / {data_json})"
                    )

    if overwrite:
        sessions.dump_json(data_json)

    return sessions


def _df2json(
    df: DataFrame,
    tz_offset_h: int,
    presentation_time_min: int,
    plenary_talk_time_min: int,
    sort_session: Callable,
) -> SessionList:
    df = df[df["Decision"] == "Accept"]
    df = df.replace(np.nan, None)  # convert NaN to None
    author_max = len([c for c in df.columns if c.startswith("First Name")])
    chair_max = len([c for c in df.columns if c.startswith("Session Chair First")])

    record_dicts = df.to_dict(orient="records")

    sessions = _dict2sessions(
        record_dicts,
        author_max,
        chair_max,
        tz_offset_h,
        presentation_time_min,
        plenary_talk_time_min,
    )

    # Sort by paper order in each ssection
    for s in sessions:
        s.papers.sort(key=lambda p: p.order)

    sessions.sort(key=sort_session)
    for s in sessions:
        print(s.code, s.start_time, s.name)

    # Save to json file
    return sessions


def load_epapers_sheet(
    filename: str,
    tz_offset_h: int,
    presentation_time_min=20,
    plenary_talk_time_min=60,
    excel_sheet_name: str | None = None,
    sort_session: Callable = default_session_sort_func,
) -> SessionList:
    """Convert Excel/CSV file to JSON file.

    Parameters
    ----------
    filename : str
        filename Excel/CSV filename.
    tz_offset_h : int
        Timezone offset in hours.
    presentation_time_min : int, optional
        Presentation time in minutes, by default 20
    plenary_talk_time_min : int, optional
        Plenary talk time in minutes, by default 60
    excel_sheet_name : str
        Sheet name in the Excel file.
    sort_session : Callable, optional
        Function to sort sessions, by default :func:`.default_session_sort_func`

    Returns
    -------
    SessionList
        List of Session objects.

    Examples
    --------
    The ``filename`` file will be an Excel/CSV file with the following columns:

    .. list-table::
        :header-rows: 1

        * - Column Name
          - Attributes of :class:`.Session`
          - Description
        * - Session Name
          - :attr:`name`
          -
        * - Session Type
          - :attr:`type`
          -
        * - Session Code
          - :attr:`code`
          -
        * - Session Location
          - :attr:`location`
          -
        * - Session Start Time
          - :attr:`start_time`
          -
        * - Session End Time
          - :attr:`end_time`
          -
        * - Session Chair First{i}
          - :attr:`chairs.name`
          - First Name of {i}-th Chair
        * - Session Chair Last{i}
          - :attr:`chairs.name`
          - Last Name of {i}-th Chair
        * - Session Chair Organization{i}
          - :attr:`chairs.organization`
          - Organization of {i}-th Chair
        * - Paper ID
          - :attr:`papers.id`
          -
        * - Paper Title
          - :attr:`papers.title`
          -
        * - Paper Order
          - :attr:`papers.order`
          -
        * - Contact First
          - :attr:`papers.contact.name`
          - First Name of Contact
        * - Contact Last
          - :attr:`papers.contact.name`
          - Last Name of Contact
        * - Contact Organization
          - :attr:`papers.contact.organization`
          -
        * - Contact Country
          - :attr:`papers.contact.country`
          -
        * - Contact Email
          - :attr:`papers.contact.email`
          -
        * - Abstract
          - :attr:`papers.abstract`
          -
        * - Keywords
          - :attr:`papers.keywords`
          -
        * - First Name{i}
          - :attr:`papers.authors.name`
          - First Name of {i}-th Author
        * - Last Name{i}
          - :attr:`papers.authors.name`
          - Last Name of {i}-th Author
        * - Organization{i}
          - :attr:`papers.authors.organization`
          - Organization of {i}-th Author
        * - Country{i}
          - :attr:`papers.authors.country`
          - Country of {i}-th Author


    Let's prepare the Excel/CSV file like the following:

    .. literalinclude:: ../py_examples/db_extract.csv
        :caption: db_extract.csv

    .. note::

        The Excel/CSV file can include unnecessary columns. The columns that are not listed above will be ignored.
        Basically, the Excel/CSV file will be generated by the conference management system automatically.

    The following code will convert the Excel/CSV file to a JSON file:

    .. literalinclude:: ../py_examples/ex_load_epapers_sheet.py

    The dumped JSON file will have the following structure:

    .. literalinclude:: ../py_examples/data.json
        :caption: data.json
        :language: json

    """
    if filename.endswith(".xlsx"):
        if excel_sheet_name is not None:
            df = read_excel(filename, sheet_name=excel_sheet_name)
        else:
            df = read_excel(filename)
    else:
        df = read_csv(filename)
    return _df2json(
        df=df,
        tz_offset_h=tz_offset_h,
        presentation_time_min=presentation_time_min,
        plenary_talk_time_min=plenary_talk_time_min,
        sort_session=sort_session,
    )


def _timestring_to_object(time: str, tz_offset_h: int) -> datetime:
    """Convert time string to datetime object with specific timezone offset."""
    return datetime.strptime(time, "%Y-%m-%d %H:%M").replace(
        tzinfo=timezone(timedelta(hours=tz_offset_h))
    )


def _dict2sessions(
    record_dicts: list[dict],
    author_max: int,
    chair_max: int,
    tz_offset_h: int,
    presentation_time_min: int,
    plenary_talk_time_min: int,
) -> SessionList:
    # Initialization
    sessions = SessionList()

    # Main loop
    for r in record_dicts:  # For each paper
        # Load authors info
        authors = [
            Person(
                name=r[f"First Name{i}"] + " " + r[f"Last Name{i}"],
                organization=r[f"Organization{i}"],
                country=r[f"Country{i}"],
            )
            for i in range(1, author_max + 1)
            if r[f"First Name{i}"] != None
        ]

        # Load paper info
        paper = Paper(
            id=r["Paper ID"],
            title=r["Paper Title"],
            order=int(r["Paper Order"]),
            contact=Person(
                name=r["Contact First"] + " " + r["Contact Last"],
                organization=r["Contact Organization"],
                country=r["Contact Country"],
                email=r["Contact Email"],
            ),
            pages=None,
            abstract=r["Abstract"],
            keywords=(r["Keywords"].replace("，", ", ").split(", ")),
            authors=authors,
            plenary=(r["Track Name"] == "Invited"),
        )

        # Load session info if not loaded yet
        try:
            # If the session is already loaded, just add the paper to the session
            idx = [s.code for s in sessions].index(r["Session Code"])

            st = sessions[idx].start_time
            if st is not None:
                paper.start_time = st + timedelta(
                    minutes=presentation_time_min * (paper.order - 1)
                )
            sessions[idx].papers.append(paper)
        except ValueError:
            # If the session is not loaded yet, load the session info
            # Load chairs info
            chairs = [
                Person(
                    name=r[f"Session Chair First{i+1}"]
                    + " "
                    + r[f"Session Chair Last{i+1}"],
                    organization=r[f"Session Chair Organization{i+1}"],
                )
                for i in range(chair_max)
                if r[f"Session Chair First{i+1}"] is not None
            ]

            # Set start time for the paper
            st = _timestring_to_object(r["Session Start Time"], tz_offset_h)
            if st is not None:
                paper.start_time = st + timedelta(
                    minutes=(
                        presentation_time_min
                        if not paper.plenary
                        else plenary_talk_time_min
                    )
                    * (paper.order - 1)
                )

            # Set session category
            # s: Special Session, r: Regular Session, p: Plenary Session, i: Invited Session
            # input will: "Plenary 1", "Invited 2", "(S3-4) xxx", "(R5-6) yyy", "(R3) zzz"
            # _cat will: ("p", None), ("i", None), ("s", 3), ("r", 5), ("r", 3)
            # _cat_o will: None, None, 4, 6, None
            if r["Session Name"][0] in ["P", "I"]:
                _cat = (str(r["Session Name"][0]).lower(), None)
                _cat_o = None
            else:
                num = str(r["Session Name"]).split(" ")[0][2:-1].split("-")
                _cat = (
                    "s" if r["Session Name"][1] == "S" else "r",
                    int(num[0]),
                )
                _cat_o = None if len(num) == 1 else int(num[1])

            session = Session(
                name=r["Session Name"],
                type=r["Session Type"],
                code=r["Session Code"],
                category=_cat,
                category_order=_cat_o,
                location=r["Session Location"],
                chairs=chairs,
                start_time=st,
                end_time=_timestring_to_object(r["Session End Time"], tz_offset_h),
                papers=[paper],
            )
            sessions.append(session)

    return sessions
