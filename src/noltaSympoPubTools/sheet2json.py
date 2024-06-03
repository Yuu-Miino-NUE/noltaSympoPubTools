from collections.abc import Callable
from string import ascii_uppercase
import numpy as np
import json
from datetime import datetime, timedelta, timezone
from pandas import DataFrame, read_excel, read_csv
from pydantic import TypeAdapter

from .models import JsonEncoder, Session, Paper, Person

__all__ = [
    "xlsx2json",
    "csv2json",
    "default_session_sort_func",
    "save_sessions",
    "update_sessions",
]


def default_session_sort_func(s: Session) -> int:
    """Default sort function for sessions.

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
    return session


def update_sessions(data_json: str, update_json: str):
    """Update session data with the update data.

    Parameters
    ----------
    data_json : str
        Input JSON filename.
    update_json : str
        Update JSON filename. The fields ``category`` and ``category_order`` are necessary to identify the session.
        If updating papers, the field ``papers`` is also necessary.
        For each updating paper, the field ``id`` is necessary to identify the paper.

    Raises
    ------
    ValueError
        If session not found.
    """
    with open(data_json) as f:
        ta = TypeAdapter(list[Session])
        sessions = ta.validate_json(json.load(f))

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

    with open(data_json, "w") as f:
        ta.dump_json(sessions)
    # save_sessions(sessions, data_json, True)


def save_sessions(
    sessions: list[Session],
    output: str,
    verbose: bool = False,
):
    """Save sessions to JSON file.

    Parameters
    ----------
    sessions : list[Session]
        List of Session objects.
    output : str
        Output JSON filename.
    verbose : bool, optional
        Print session counts, by default False.
    """
    kwargs = {
        "indent": 4,
        "cls": JsonEncoder,
        "ensure_ascii": False,
    }
    json.dump(obj=sessions, fp=open(output, "w"), **kwargs)
    if verbose:
        print("Session counts:", len(sessions))


def _df2json(
    df: DataFrame,
    output: str,
    tz_offset_h: int,
    author_max: int,
    chair_max: int,
    presentation_time_min: int,
    plenary_talk_time_min: int,
    sort_session: Callable,
):
    df = df[df["Decision"] == "Accept"]
    df = df.replace(np.nan, None)  # convert NaN to None
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
    save_sessions(sessions, output, True)


def xlsx2json(
    input: str,
    sheet_name: str,
    output: str,
    tz_offset_h: int,
    author_max: int = 12,
    chair_max: int = 2,
    presentation_time_min=20,
    plenary_talk_time_min=60,
    sort_session: Callable = default_session_sort_func,
):
    """Convert Excel file to JSON file.

    Parameters
    ----------
    input : str
        Input Excel filename.
    sheet_name : str
        Sheet name in the Excel file.
    output : str
        Output JSON filename.
    tz_offset_h : int
        Timezone offset in hours.
    author_max : int, optional
        Max number of Authors, by default 12
    chair_max : int, optional
        Max number of Chair person, by default 2
    presentation_time_min : int, optional
        Presentation time in minutes, by default 20
    plenary_talk_time_min : int, optional
        Plenary talk time in minutes, by default 60
    sort_session : Callable, optional
        Function to sort sessions, by default default_session_sort_funcs
    """
    df = read_excel(input, sheet_name=sheet_name)
    _df2json(
        df=df,
        output=output,
        tz_offset_h=tz_offset_h,
        author_max=author_max,
        chair_max=chair_max,
        presentation_time_min=presentation_time_min,
        plenary_talk_time_min=plenary_talk_time_min,
        sort_session=sort_session,
    )


def csv2json(
    input: str,
    output: str,
    tz_offset_h: int,
    author_max: int = 12,
    chair_max: int = 2,
    presentation_time_min: int = 20,
    plenary_talk_time_min: int = 60,
    sort_session: Callable = default_session_sort_func,
):
    """Convert CSV file to JSON file.

    Parameters
    ----------
    input : str
        Input CSV filename.
    output : str
        Output JSON filename.
    tz_offset_h : int
        Timezone offset in hours.
    author_max : int, optional
        Max number of Authors, by default 12
    chair_max : int, optional
        Max number of Chair person, by default 2
    presentation_time_min : int, optional
        Presentation time in minutes, by default 20
    plenary_talk_time_min : int, optional
        Plenary talk time in minutes, by default 60
    sort_session : Callable, optional
        Function to sort sessions, by default default_session_sort_func
    """
    df = read_csv(input)
    _df2json(
        df=df,
        output=output,
        tz_offset_h=tz_offset_h,
        author_max=author_max,
        chair_max=chair_max,
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
) -> list[Session]:
    # Initialization
    sessions: list[Session] = []

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
