import json
import csv
from typing import Sequence

from ..sheet2json import Session
from ..json2tex import SSOrganizer

from ._classes import AsList, MSession, MPaper, MCommon, Award, CommonInfo

__all__ = [
    "load_common",
    "load_papers",
    "load_sessions",
    "save_data_as_csv",
]


def load_sessions(
    data_json: str, ss_organizers_json: str, common_json: str
) -> list[MSession]:
    """Load session information from JSON file.

    Parameters
    ----------
    data_json : str
        Input JSON file path.
    ss_organizers_json : str
        Input JSON file path for session organizers.
    common_json : str
        Input JSON file path for common information.

    Returns
    -------
    list[MSession]
        List of session information.
    """

    with open(data_json, "r") as f:
        s_data = [Session(**s) for s in json.load(f)]

    with open(ss_organizers_json, "r") as f:
        ss_org_data = [SSOrganizer(**sso) for sso in json.load(f)]

    with open(common_json, "r") as f:
        common_data = CommonInfo(**json.load(f))
        cities = common_data.event_city
        venues = common_data.event_venue

    sessions: list[MSession] = []

    for ss in s_data:
        if ss.category[0] != "s":
            organizers = []
            org_affils = []
        else:
            try:
                idx = [d.category for d in ss_org_data].index(ss.category)
                organizers = [o.name for o in ss_org_data[idx].organizers]
                org_affils = [o.organization for o in ss_org_data[idx].organizers]
            except ValueError:
                print(f"Session {ss.code} not found in {ss_organizers_json}")
                raise

        session = MSession(
            comment="",
            number=ss.code,
            name=ss.name,
            date=ss.start_time.date(),
            organizers=organizers,
            org_affils=org_affils,
            chairs=[c.name for c in ss.chairs],
            chair_affils=[c.organization for c in ss.chairs],
            cities=cities,
            venues=venues,
        )
        sessions.append(session)

    return sessions


def save_data_as_csv(filename: str, data: Sequence[AsList], template: str):
    """Save data as CSV file.

    Parameters
    ----------
    filename : str
        Output CSV file path.
    data : Sequence[AsList]
        Data to be saved.
    template : str
        Template CSV file path.
    """

    with open(template, "r") as f:
        reader = csv.reader(f)
        headers = [next(reader), next(reader)]

    with open(filename, "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers[0])
        writer.writerow(headers[1])
        for d in data:
            writer.writerow(d.as_list())


def load_papers(data_json: str, award_json: str) -> list[MPaper]:
    """Load paper information from JSON file.

    Parameters
    ----------
    data_json : str
        Input JSON file path.
    award_json : str
        Input JSON file path for awards.

    Returns
    -------
    list[MPaper]
        List of paper information.
    """

    with open(data_json, "r") as f:
        s_data = [Session(**s) for s in json.load(f)]

    with open(award_json, "r") as f:
        a_data = [Award(**a) for a in json.load(f)]

    papers: list[MPaper] = []

    for ss in s_data:
        for p in ss.papers:
            number = ss.code + str(p.order)
            filename = number + ".pdf" if p.pages is not None else ""

            try:
                idx = [a.id for a in a_data].index(number)
                awards = a_data[idx].awards
            except ValueError:
                awards = []

            paper = MPaper(
                comment="",
                title=p.title,
                filename=filename,
                abstract=p.abstract,
                keywords=[k for k in p.keywords if k != "-"],
                pages=p.pages,
                session=ss.code,
                number=number,
                awards=awards,
                authors=[a.name for a in p.authors],
                affils=[a.organization for a in p.authors],
            )
            papers.append(paper)

    return papers


def load_common(common_json: str) -> MCommon:
    """Load common information from JSON file.

    Parameters
    ----------
    common_json : str
        Input JSON file path.

    Returns
    -------
    MCommon
        Common information.
    """
    with open(common_json, "r") as f:
        data = CommonInfo(**json.load(f))

    return MCommon(
        comment="",
        conf_abbr=data.conf_abbr,
        year=str(data.year),
        event_name=data.event_name,
        event_date=(
            data.event_date[0],
            data.event_date[1],
        ),
        event_city=data.event_city,
        event_venue=data.event_venue,
        event_web_url=data.event_web_url,
        cooperators=data.cooperators,
        publication=data.publication,
        date_published=data.date_published,
        publisher=data.publisher,
    )
