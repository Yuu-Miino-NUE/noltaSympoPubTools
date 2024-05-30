import json
import csv
from typing import Sequence

from .models import (
    MetaSession,
    MetaArticle,
    MetaCommon,
    Metadata,
    CommonInfo,
    Award,
    Session,
    SSOrganizer,
)

__all__ = [
    "load_common",
    "load_articles",
    "load_sessions",
    "save_data_as_csv",
]


def save_data_as_csv(filename: str, data: Sequence[Metadata], template: str):
    """Save metadata as CSV file.

    Parameters
    ----------
    filename : str
        Output CSV file path.
    data : Sequence[Metadata]
        Metadata to be saved.
    template : str
        Template CSV file path. The template file should have the same structure as the output CSV file.
        Required fields are dependent on the metadata type, but the first two rows should be the headers.

    See Also
    --------
    .MetaCommon: Data class for common information
    .MetaSession: Data class for session
    .MetaArticle: Data class for paper
    .load_common: Load common information from JSON file
    .load_sessions: Load session information from JSON file
    .load_articles: Load paper information from JSON file
    """

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
        for d in data:
            writer.writerow(d.as_list())


def load_sessions(
    data_json: str, ss_organizers_json: str, common_json: str
) -> list[MetaSession]:
    """Load session information from JSON file.

    Parameters
    ----------
    data_json : str
        Input JSON file path. The JSON file should have the structure of :class:`.Session`.

    ss_organizers_json : str
        Input JSON file path for session organizers. The JSON file should have the structure of :class:`.SSOrganizer`.

    common_json : str
        Input JSON file path for common information. The JSON file should have the structure of :class:`.CommonInfo`.

    Returns
    -------
    list[MetaSession]
        List of session information, each of which is an instance of :class:`.MetaSession`.

    Examples
    --------
    The JSON file to pass to `data_json` should have the following structure:

    .. literalinclude:: /py_examples/ex_data.json
        :caption: data.json
        :language: json

    The JSON file to pass to `ss_organizers_json` should have the following structure:

    .. literalinclude:: /py_examples/ex_ss_organizers.json
        :caption: ss_organizers.json
        :language: json

    The JSON file to pass to `common_json` should have the following structure:

    .. literalinclude:: /py_examples/ex_common.json
        :caption: common.json
        :language: json

    Here is an example of how to use the :func:`load_sessions` function.

    .. literalinclude:: /py_examples/ex_load_sessions.py

    For :func:`save_data_as_csv`, the template file should have the following structure:

    .. code-block::
        :caption: session_template.csv

        #,セッション番号,セッション,開催日,主催者1,機関1(主),座長1,機関1(座),開催都市,会場
        #,Session identifier,Name of session,Date of session,Organizer 1,Affiliation 1 (Org. 1),Chairperson 1,Affiliation 1 (Chair. 1),City,Venue

    See Also
    --------
    .MetaSession: Data class for session
    .Session: Data class for session
    .SSOrganizer: Data class for session
    .CommonInfo: Data class for common information
    .save_data_as_csv: Save metadata as CSV file
    """

    with open(data_json, "r") as f:
        s_data = [Session(**s) for s in json.load(f)]

    with open(ss_organizers_json, "r") as f:
        ss_org_data = [SSOrganizer(**sso) for sso in json.load(f)]

    with open(common_json, "r") as f:
        common_data = CommonInfo(**json.load(f))
        cities = common_data.event_city
        venues = common_data.event_venue

    sessions: list[MetaSession] = []

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

        session = MetaSession(
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


def load_articles(data_json: str, award_json: str) -> list[MetaArticle]:
    """Load article information from JSON file.

    Parameters
    ----------
    data_json : str
        Input JSON file path. The JSON file should have the structure of :class:`.Session`.
    award_json : str
        Input JSON file path for awards. The JSON file should have the structure of :class:`.Award`.

    Returns
    -------
    list[MetaArticle]
        List containig article information, each of which is an instance of :class:`.MetaArticle`.

    Examples
    --------
    The JSON file to pass to `data_json` should have the following structure:

    .. literalinclude:: /py_examples/ex_data.json
        :caption: data.json
        :language: json

    The JSON file to pass to `award_json` should have the following structure:

    .. literalinclude:: /py_examples/ex_award.json
        :caption: award.json
        :language: json

    Here is an example of how to use the :func:`load_articles` function.

    .. literalinclude:: /py_examples/ex_load_articles.py

    For :func:`save_data_as_csv`, the template file should have the following structure:

    .. code-block::
        :caption: article_template.csv

        #,タイトル,本文ファイル名,要約,キーワード,開始ページ,終了ページ,セッション番号,volume番号,番号,表彰,"著者1@@著者2@@著者3@@著者4@@著者5@@著者6@@著者7@@著者8@@著者9@@著者10@@著者11@@著者12@@著者13@@著者14@@著者15","機関1@@機関2@@機関3@@機関4@@機関5@@機関6@@機関7@@機関8@@機関9@@機関10@@機関11@@機関12@@機関13@@機関14@@機関15"
        #,Title,File name of article body,Abstract,Keyword(s),Start page,End page,Session identifier,Volume of publication,Article identifier,Award,"Author 1@@Author 2@@Author 3@@Author 4@@Author 5@@Author 6@@Author 7@@Author 8@@Author 9@@Author 10@@Author 11@@Author 12@@Author 13@@Author 14@@Author 15","Affiliation 1@@Affiliation 2@@Affiliation 3@@Affiliation 4@@Affiliation 5@@Affiliation 6@@Affiliation 7@@Affiliation 8@@Affiliation 9@@Affiliation 10@@Affiliation 11@@Affiliation 12@@Affiliation 13@@Affiliation 14@@Affiliation 15"

    See Also
    --------
    .MetaArticle: Data class for paper
    .Session: Data class for session
    .Award: Data class for awards
    .save_data_as_csv: Save metadata as CSV file

    """

    with open(data_json, "r") as f:
        s_data = [Session(**s) for s in json.load(f)]

    with open(award_json, "r") as f:
        a_data = [Award(**a) for a in json.load(f)]

    papers: list[MetaArticle] = []

    for ss in s_data:
        for p in ss.papers:
            number = ss.code + str(p.order)
            filename = number + ".pdf" if p.pages is not None else ""

            try:
                idx = [a.id for a in a_data].index(number)
                awards = a_data[idx].awards
            except ValueError:
                awards = []

            paper = MetaArticle(
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


def load_common(common_json: str) -> MetaCommon:
    """Load common information from JSON file.

    Parameters
    ----------
    common_json : str
        Input JSON file path. The JSON file should have the structure of :class:`.CommonInfo`.

    Returns
    -------
    MetaCommon
        Common information.

    Examples
    --------
    Here is an example of how to use the :func:`load_common` function.

    .. literalinclude:: /py_examples/ex_load_common.py

    The template file should have the following structure:

    .. code-block::
        :caption: common_template.csv

        #,セッション番号,セッション,開催日,主催者1,機関1(主),座長1,機関1(座),開催都市,会場
        #,Session identifier,Name of session,Date of session,Organizer 1,Affiliation 1 (Org. 1),Chairperson 1,Affiliation 1 (Chair. 1),City,Venue

    See Also
    --------
    .MetaCommon: Data class for common information
    .save_data_as_csv: Save metadata as CSV file
    """

    with open(common_json, "r") as f:
        data = CommonInfo(**json.load(f))

    return MetaCommon(
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
