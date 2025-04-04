import json, os
from datetime import datetime

from .models import Session, Person, SSOrganizer


def _template(path: str):
    return os.path.join(os.path.dirname(__file__), "tex_templates", path)


def _escape_tex(tex: str) -> str:
    return (
        tex.replace("\\&", "&")
        .replace("&", "\\&")
        .replace("\\%", "%")
        .replace("%", "\\%")
    )


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


def json2ss_tex(
    data_json: str,
    ss_organizers_json: str,
    output: str,
    session_name_prefix_cnt: int = 0,
):
    """Extracts session data from ``data_json`` and ``ss_organizers_json`` and generates a LaTeX file.

    Parameters
    ----------
    data_json : str
        Input JSON file path. The JSON file should have the structure of :class:`.Session`.
    ss_organizers_json : str
        Input JSON file path for session organizers. The JSON file should have the structure of :class:`.SSOrganizer`.
    output : str
        Output TeX file path.
    session_name_prefix_cnt : int, optional
        The number of words to be removed from the beginning of the session name, by default 0.

    Examples
    --------
    Prepare JSON files with the following structure:

    .. literalinclude:: /py_examples/data_with_pages.json
        :caption: data.json
        :language: json

    .. literalinclude:: /py_examples/ss_organizers.json
        :caption: ss_organizers.json
        :language: json

    Here is an example of how to use the :func:`json2ss_tex` function.

    .. literalinclude:: /py_examples/ex_json2ss_tex.py

    The output TeX file will have the following structure:

    .. literalinclude:: /py_examples/ss_list.tex
        :caption: ss_list.tex
        :language: latex

    The generated LaTeX file includes 1 manual environment ``ssSessionTabular`` and 1 manual command ``\\ssOrgTabular``.
    By defining them properly, you can include the generated LaTeX file in your LaTeX document.

    See Also
    --------
    .Session: Data class for session
    .SSOrganizer: Data class for session
    """
    with open(data_json) as f:
        data = [Session(**s) for s in json.load(f)]
    with open(ss_organizers_json) as f:
        orgs_data = [SSOrganizer(**sso) for sso in json.load(f)]

    s_texs: list[str] = []

    for rs in orgs_data:
        try:
            _sessions = [d for d in data if d.code in rs.session_codes]
            sessions_tex = "\\\\\n".join(
                [
                    _ssRecordTex(
                        _s.code, " ".join(_s.name.split(" ")[session_name_prefix_cnt:])
                    )
                    for _s in _sessions
                ]
            )
            ss_orgs = _ssOrgsTex(rs.organizers)
            s_texs.append(_ssSessionTex(sessions_tex, ss_orgs))
        except ValueError:
            print(f"Session {rs.session_codes} not found in orgs.json")
            continue

    with open(output, "w") as f:
        f.write("\\ssbreak\n".join(s_texs))


def _pEntryTex(
    id: str,
    title: str,
    page_from: int,
    page_to: int,
    authors: list[Person],
    indices_tex: str,
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
        "INDICES": indices_tex,
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


def _make_indices_tex(author: Person, session_code: str):
    name_list = author.name.split(" ")
    f_name = name_list[-1] + ", " + " ".join(name_list[:-1])
    return "\\customindex{" + f_name + "}{" + session_code + "}"


def json2papers_tex(data_json: str, output: str):
    """Extract papers information from JSON file and generate TeX file.

    Parameters
    ----------
    data_json : str
        Input JSON file path. The JSON file should have the structure of :class:`.Session`.
    output : str
        Output TeX file path.

    Examples
    --------
    Prepare a JSON file with the following structure:

    .. literalinclude:: /py_examples/data_with_pages.json
        :caption: data.json
        :language: json

    Here is an example of how to use the :func:`.json2papers_tex` function.

    .. literalinclude:: /py_examples/ex_json2papers_tex.py

    The output TeX file will have the following structure:

    .. literalinclude:: /py_examples/papers_information.tex
        :caption: papers_information.tex
        :language: latex

    The generated LaTeX file includes 1 manual environment ``session`` and 1 manual command ``\\pEntry``.
    By defining them properly, you can include the generated LaTeX file in your LaTeX document.

    See Also
    --------
    .Session: Data class for session
    """
    with open(data_json) as f:
        data = [Session(**s) for s in json.load(f)]

    s_texs: list[str] = []
    for s in data:
        p_texs = [
            _pEntryTex(
                id=s.code + f"{i+1}",
                title=p.title,
                page_from=p.pages[0] if p.pages is not None else 0,
                page_to=p.pages[1] if p.pages is not None else 0,
                indices_tex="".join(
                    [_make_indices_tex(a, s.code + f"{i+1}") for a in p.authors]
                ),
                authors=p.authors,
                abstract=p.abstract,
                paper_id=str(p.id),
                keywords=p.keywords if p.keywords is not None else [],
                plenary=p.plenary,
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
    spanel = spanel.replace("NAME", _escape_tex(name))
    spanel = spanel.replace("CHAIRS", _chairs)

    return spanel


def _timeslotTex(start_time: datetime, end_time: datetime):
    with open(_template("timeslot.tex")) as f:
        timeslot = f.read()

    timeslot = timeslot.replace("START_TIME", start_time.strftime("%H:%M"))
    timeslot = timeslot.replace("END_TIME", end_time.strftime("%H:%M"))

    return timeslot


def json2spanel_texs(
    data_json: str,
    output_dir: str,
    first_room_code: str | None = None,
    final_room_code: str | None = None,
):
    """Extracts schedule data from data_json and generates LaTeX files.

    Parameters
    ----------
    data_json : str
        Input JSON file path. The JSON file should have the structure of :class:`.Session`.
    output_dir : str
        Output directory path.
    first_room_code : str, optional
        The first room code, by default None. If None, the first room code is the minimum ASCII code of the room codes supplied.
    final_room_code : str, optional
        The final room code, by default None. If None, the final room code is the maximum ASCII code of the room codes supplied.

    Examples
    --------
    Prepare a JSON file with the following structure:

    .. literalinclude:: /py_examples/data_with_pages.json
        :caption: data.json
        :language: json

    Here is an example of how to use the :func:`json2spanel_texs` function.

    .. literalinclude:: /py_examples/ex_json2spanel_texs.py

    The output TeX files will have the following structure:

    .. literalinclude:: /py_examples/spanels/A2L.tex
        :caption: spanels/A2L.tex
        :language: latex

    The generated LaTeX file includes 3 manual commands: ``\\timeslot``, ``\\nosession``, and ``\\spanel``.
    By defining them properly, you can include the generated LaTeX file in your LaTeX document.

    See Also
    --------
    .Session: Data class for session

    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(data_json) as f:
        data = [Session(**s) for s in json.load(f)]

    class _SessionTeX:
        def __init__(self, order: int, tex: str):
            self.order = order
            self.tex = tex

    out_dict: dict[str, list[_SessionTeX]] = {}
    smin = int(ord(first_room_code)) if first_room_code is not None else 10000
    smax = int(ord(final_room_code)) if final_room_code is not None else -1
    for session in data:
        _tex = "& " + _spanelTex(
            session.code, session.name, [c.name for c in session.chairs]
        )

        code_group, order = session.code.split("-")
        if code_group not in out_dict:
            out_dict[code_group] = [
                _SessionTeX(0, _timeslotTex(session.start_time, session.end_time))
            ]

        order = int(ord(order))
        out_dict[code_group].append(_SessionTeX(order, _tex))
        smin = min(smin, order)
        smax = max(smax, order)

    if smin > smax:
        raise ValueError("Order of sessions is not correct.")

    for code_group, stexs in out_dict.items():
        _orders = [t.order for t in stexs]
        for r in range(smin, smax + 1):
            if r not in _orders:
                stexs.insert(r - smin + 1, _SessionTeX(r, "& \\nosession"))

        with open(f"{output_dir}/{code_group}.tex", "w") as f:
            f.write("\n".join([t.tex for t in stexs]))
