import json
from pydantic import BaseModel

from sheet2json import Session, Person
from .tools import template as _template, escape_tex as _escape_tex

__all__ = ["json2ssTex", "SSOrganizer"]


class SSOrganizer(BaseModel):
    category: tuple
    title: str
    organizers: list[Person]


def _ssRecordTex(code: str, name: str):
    with open(_template("ssRecord.tex")) as f:
        ssRecord = f.read()
    ssRecord = ssRecord.replace("CODE", code)
    ssRecord = ssRecord.replace("NAME", _escape_tex(name))
    return ssRecord


def _ssOrgsTex(organizers: list[Person]):
    with open(_template("ssOrgs.tex")) as f:
        ssOrgs = f.read()

    if len(organizers) == 1:
        _organizers = organizers[0].name + " (" + organizers[0].organization + ")"
        heading = "Organizer"
    else:
        _organizers = (
            ", ".join([o.name + " (" + o.organization + ")" for o in organizers[0:-1]])
            + " and "
            + organizers[-1].name
            + " ("
            + organizers[-1].organization
            + ")"
        )
        heading = "Organizers"

    ssOrgs = ssOrgs.replace("HEADING", heading)
    ssOrgs = ssOrgs.replace("ORGANIZERS", _escape_tex(_organizers))
    return ssOrgs


def _ssSessionTex(sessions: str, ss_orgs: str):
    with open(_template("ssSession.tex")) as f:
        ssSession = f.read()
    ssSession = ssSession.replace("SESSIONS", sessions)
    ssSession = ssSession.replace("SS_ORGS", ss_orgs)
    return ssSession


def json2ssTex(data_json: str, ss_organizers_json: str, output: str):
    """Extracts session data from data_json and ss_organizers_json and generates a LaTeX file.

    Parameters
    ----------
    data_json : str
        Input JSON file path.
    ss_organizers_json : str
        Input JSON file path for session organizers.
    output : str
        Output TeX file path.
    """
    with open(data_json) as f:
        ss_data = [
            ss for ss in [Session(**s) for s in json.load(f)] if ss.category[0] == "s"
        ]
    with open(ss_organizers_json) as f:
        orgs_data = [SSOrganizer(**sso) for sso in json.load(f)]

    s_texs: list[str] = []

    for rs in orgs_data:
        try:
            _sessions = [s for s in ss_data if s.category == rs.category]
            sessions_tex = "\\\\\n".join(
                [
                    _ssRecordTex(_s.code, " ".join(_s.name.split(" ")[1:]))
                    for _s in _sessions
                ]
            )
            ss_orgs = _ssOrgsTex(rs.organizers)
            s_texs.append(_ssSessionTex(sessions_tex, ss_orgs))
        except ValueError:
            print(f"Session {rs.category} not found in orgs.json")
            continue

    with open(output, "w") as f:
        f.write("\\ssbreak\n".join(s_texs))
