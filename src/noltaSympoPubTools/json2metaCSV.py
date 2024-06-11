"""
.. _国際会議メタデータ仕様書: https://www.ieice.org/jpn/books/pdf/metadata.pdf

Note
----
IEICE における 国際会議メタデータ仕様書_ に基づいて，メタデータを生成するためのツールです．
"""

import json

from .models import (
    MetaSession,
    MetaSessionList,
    MetaArticle,
    MetaArticleList,
    MetaCommon,
    CommonInfo,
    AwardList,
    SessionList,
    SSOrganizerList,
)

__all__ = ["load_common", "load_articles", "json2meta_sessions"]


def json2meta_sessions(
    data_json: str, ss_organizers_json: str, common_json: str
) -> MetaSessionList:
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
    MetaSessionList
        List of session information, each of which is an instance of :class:`.MetaSession`.

    Examples
    --------
    Each record in the data JSON file should have the structure of :class:`.Session`.

    .. literalinclude:: /py_examples/data_with_pages.json
        :caption: data.json
        :language: json

    Each record in the session organizers JSON file should have the structure of :class:`.SSOrganizer`.

    .. literalinclude:: /py_examples/ss_organizers.json
        :caption: ss_organizers.json
        :language: json

    The JSON file to pass to `common_json` should have the structure of :class:`.CommonInfo`.

    .. literalinclude:: /py_examples/common.json
        :caption: common.json
        :language: json

    Here is an example of how to use the :func:`json2meta_sessions` function.

    .. literalinclude:: /py_examples/ex_json2meta_sessions.py

    For dumping the metadata CSV file, the template file should have the following structure:

    .. literalinclude:: /py_examples/session_template.csv
        :caption: session_template.csv
        :language: none

    The output CSV file will have the following structure:

    .. literalinclude:: /py_examples/metadata_session.csv
        :caption: metadata_session.csv
        :language: none

    See Also
    --------
    .MetaSession: Data class for session
    .MetaSessionList: List of session metadata
    .MetadataList.dump_csv: Dump metadata to CSV file
    .Session: Data class for session
    .SSOrganizer: Data class for session
    .CommonInfo: Data class for common information
    """

    with open(data_json, "r") as f:
        s_data = SessionList(json.load(f))

    with open(ss_organizers_json, "r") as f:
        ss_org_data = SSOrganizerList(json.load(f))

    with open(common_json, "r") as f:
        common_data = CommonInfo(**json.load(f))
        cities = common_data.event_city
        venues = common_data.event_venue

    sessions = MetaSessionList()

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


def load_articles(data_json: str, award_json: str) -> MetaArticleList:
    """Load article information from JSON file.

    Parameters
    ----------
    data_json : str
        Input JSON file path. The JSON file should have the structure of :class:`.Session`.
    award_json : str
        Input JSON file path for awards. The JSON file should have the structure of :class:`.Award`.

    Returns
    -------
    MetaArticleList
        List containig article information, each of which is an instance of :class:`.MetaArticle`.

    Examples
    --------
    Each record in the data JSON file should have the structure of :class:`.Session`.

    .. literalinclude:: /py_examples/data_with_pages.json
        :caption: data.json
        :language: json

    Each record in the award JSON file should have the structure of :class:`.Award`.

    .. literalinclude:: /py_examples/awards.json
        :caption: award.json
        :language: json

    Here is an example of how to use the :func:`load_articles` function.

    .. literalinclude:: /py_examples/ex_load_articles.py

    For dumping the metadata CSV file, the template file should have the following structure:

    .. literalinclude:: /py_examples/article_template.csv
        :caption: article_template.csv
        :language: none


    The output CSV file will have the following structure:

    .. literalinclude:: /py_examples/metadata_article.csv
        :caption: metadata_article.csv
        :language: none

    See Also
    --------
    .MetaArticle: Data class for paper
    .MetaArticleList: List of metadata
    .MetadataList.dump_csv: Dump metadata to CSV file
    .Session: Data class for session
    .Award: Data class for awards

    """

    with open(data_json, "r") as f:
        s_data = SessionList(json.load(f))

    with open(award_json, "r") as f:
        a_data = AwardList(json.load(f))

    papers = MetaArticleList()

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
    The JSON file to pass to `common_json` should have the structure of :class:`.CommonInfo`.

    .. literalinclude:: /py_examples/common.json
        :caption: common.json
        :language: json

    Here is an example of how to use the :func:`load_common` function.

    .. literalinclude:: /py_examples/ex_load_common.py

    For dumping the metadata CSV file, the template file should have the following structure:

    .. literalinclude:: /py_examples/common_template.csv
        :caption: common_template.csv
        :language: none

    The output CSV file will have the following structure:

    .. literalinclude:: /py_examples/metadata_common.csv
        :caption: metadata_common.csv
        :language: none

    See Also
    --------
    .MetaCommon: Data class for common information
    .Metadata: Base class for metadata
    .Metadata.dump_csv: Dump metadata to CSV file
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
