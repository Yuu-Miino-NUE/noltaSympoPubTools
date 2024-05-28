from collections.abc import Callable
from string import ascii_uppercase
import numpy as np
import json
from datetime import datetime, date, time
from pandas import DataFrame, read_excel, read_csv

from .core import _dict2sessions

from .classes import Session, Paper, Person

__all__ = [
    "xlsx2json",
    "csv2json",
    "default_session_sort_func",
    "save_sessions",
    "update_sessions",
]


class _JsonEncoder(json.JSONEncoder):
    """JSON encoder for IterItems object."""

    def default(self, obj):
        if isinstance(obj, (Person, Paper, Session)):
            return dict(obj)
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()
        return super().default(obj)


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
        sessions = [Session(**s) for s in json.load(f)]

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

    save_sessions(sessions, data_json, True)


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
        "cls": _JsonEncoder,
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
