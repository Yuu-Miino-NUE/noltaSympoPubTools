import json, os
from datetime import datetime

from ..sheet2json import Session
from ._utils import template as _template

__all__ = ["json2spanelTex"]


# 1: Session ID, #2: Title, #3: Chair Name Information
def _spanelTex(code: str, name: str, chairnames: list[str]):
    with open(_template("spanel.tex")) as f:
        spanel = f.read()

    _chairnames = ["\\mbox{" + c + "}" for c in chairnames]

    _chairs = ("Chair: " if len(_chairnames) == 1 else "Chairs: ") + " and ".join(
        _chairnames
    )
    if len(_chairnames) == 0:
        _chairs = "\\tba"

    spanel = spanel.replace("CODE", code)
    spanel = spanel.replace("NAME", name)
    spanel = spanel.replace("CHAIRS", _chairs)

    return spanel


def _timeslotTex(start_time: datetime, end_time: datetime):
    with open(_template("timeslot.tex")) as f:
        timeslot = f.read()

    timeslot = timeslot.replace("START_TIME", start_time.strftime("%H:%M"))
    timeslot = timeslot.replace("END_TIME", end_time.strftime("%H:%M"))

    return timeslot


def json2spanelTex(data_json: str, output_dir: str):
    """Extracts schedule data from data_json and generates LaTeX files.

    Parameters
    ----------
    data_json : str
        Input JSON file path.
    output_dir : str
        Output directory path.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(data_json) as f:
        data = [Session(**s) for s in json.load(f)]

    out_dict: dict[str, list[dict[str, str]]] = {}
    smax = 1
    for session in data:
        _tex = "& " + _spanelTex(
            session.code, session.name, [c.name for c in session.chairs]
        )

        if (code := session.code[0:-2]) not in out_dict:
            out_dict[code] = [
                {
                    "order": "0",
                    "tex": _timeslotTex(session.start_time, session.end_time),
                }
            ]

        out_dict[code].append({"order": session.code[-1], "tex": _tex})
        smax = max(smax, int(session.code[-1]))

    for code, texs in out_dict.items():
        _orders = [t["order"] for t in texs]
        for r in range(1, smax + 1):
            if str(r) not in _orders:
                texs.insert(r, {"order": str(r), "tex": "& \\nosession"})

        with open(f"{output_dir}/{code}.tex", "w") as f:
            f.write("\n".join([t["tex"] for t in texs]))
