from datetime import datetime, timezone, timedelta

from .classes import Person, Paper, Session

__all__ = ["_dict2sessions"]


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
