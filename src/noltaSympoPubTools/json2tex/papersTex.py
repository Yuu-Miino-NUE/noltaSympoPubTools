import json
from datetime import datetime

from sheet2json import Session, Person
from .tools import escape_tex as _escape_tex, template as _template


__all__ = ["json2papersTex"]


def _pEntryTex(
    id: str,
    title: str,
    page_from: int,
    page_to: int,
    authors: list[Person],
    abstract: str,
    paper_id: str,
    keywords: list[str],
    plenary: bool,
):
    _authors = ", ".join([a.name + ", (" + a.organization + ")" for a in authors])
    _keywords = ", ".join(keywords) if keywords is not None else ""
    _abstract = abstract if abstract != "-" else ""

    repl = {
        "PID": id,
        "TITLE": title,
        "AUTHORS": _authors,
        "ABSTRACT": _abstract,
        "PAGE_FROM": page_from,
    }

    if not plenary:
        with open(_template("pEntry.tex")) as f:
            pEntry = f.read()
        repl |= {
            "PAGE_TO": page_to,
            "KEYWORDS": _keywords,
            "PAPER_ID": paper_id,
        }
    else:
        with open(_template("pEntryPlenary.tex")) as f:
            pEntry = f.read()

    for k in repl:
        pEntry = pEntry.replace(k, str(repl[k]))

    return pEntry


def _sessionTex(
    id: str,
    title: str,
    start_time: datetime,
    end_time: datetime,
    place: str,
    chairs: list[Person],
    p_texs: list[str],
):
    if len(chairs) == 0:
        _chairs = "\\tba"
    else:
        _chairs = ", ".join([c.name + " (" + c.organization + ")" for c in chairs])
    _p_texs = "\n".join(p_texs)
    _date = start_time.strftime("%Y/%m/%d~~%H:%M") + "--" + end_time.strftime("%H:%M")

    with open(_template("session.tex")) as f:
        session = f.read()

    for b, a in zip(
        ["SID", "TITLE", "DATE", "PLACE", "CHAIRS", "P_ENTRIES"],
        [id, title, _date, place, _chairs, _p_texs],
    ):
        session = session.replace(b, str(a))

    return session


def json2papersTex(data_json: str, output: str):
    """Extract papers information from JSON file and generate TeX file.

    Parameters
    ----------
    data_json : str
        Input JSON file path.
    output : str
        Output TeX file path.
    """
    with open(data_json) as f:
        data = [Session(**s) for s in json.load(f)]

    s_texs: list[str] = []
    for s in data:
        p_texs = [
            _pEntryTex(
                s.code + f"{i+1}",
                p.title,
                p.pages[0] if p.pages is not None else 0,
                p.pages[1] if p.pages is not None else 0,
                p.authors,
                p.abstract,
                str(p.id),
                p.keywords if p.keywords is not None else [],
                p.plenary,
            )
            for i, p in enumerate(s.papers)
        ]
        s_texs.append(
            _sessionTex(
                s.code, s.name, s.start_time, s.end_time, s.location, s.chairs, p_texs
            )
        )
    with open(output, "w") as f:
        f.write(_escape_tex("".join(s_texs)))
