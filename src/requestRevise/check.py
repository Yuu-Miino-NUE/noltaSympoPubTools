import os, json

from . import ReviseItem


def get_revised_ids(revised_pdfs_dir: str) -> set[str]:
    """Get the IDs of revised papers from the directory of revised PDFs.

    Parameters
    ----------
    revised_pdfs_dir : str
        Directory path containing revised PDFs.

    Returns
    -------
    set[str]
        Set of paper IDs.
    """
    revised_ids = []
    for _, _, files in os.walk(revised_pdfs_dir):
        for file in files:
            if file.endswith(".pdf"):
                revised_ids.append(str(file[:-4]))
    return set(revised_ids)


def get_all_ids(input_json: str) -> set[str]:
    """Get all paper IDs from the JSON file.

    Parameters
    ----------
    input_json : str
        Path to the JSON file.

    Returns
    -------
    set[str]
        Set of paper IDs.
    """
    all_ids = []
    with open(input_json) as f:
        data = [ReviseItem(**r) for r in json.load(f)]
        for item in data:
            all_ids.append(str(item.paper_id))
    return set(all_ids)


def get_records_by_ids(input_json: str, ids: set[str]) -> list[ReviseItem]:
    """Get records by paper IDs.

    Parameters
    ----------
    input_json : str
        Path to the JSON file.
    ids : set[str]
        Set of paper IDs.

    Returns
    -------
    list[ReviseItem]
        List of records.

    Raises
    ------
    ValueError
        If a paper ID is not found in the JSON file.
    """
    ret = []
    with open(input_json) as f:
        data = [ReviseItem(**r) for r in json.load(f)]

    for id in ids:
        try:
            idx = [item.paper_id for item in data].index(int(id))
            ret.append(data[idx])
        except ValueError:
            raise ValueError(f"Paper ID {id} not found in the JSON file.")

    return ret


def show_revise_summary(
    all_ids: set[str], revised_ids: set[str], missing_ids: set[str]
):
    """Show the summary of revised papers.

    Parameters
    ----------
    all_ids : set[str]
        Set of all paper IDs.
    revised_ids : set[str]
        Set of revised paper IDs.
    missing_ids : set[str]
        Set of missing paper IDs.
    """
    rate = len(revised_ids) / len(all_ids) * 100
    print(
        len(all_ids),
        "=",
        len(missing_ids),
        "+",
        len(revised_ids),
        f"({rate:.2f} % revised)",
        end="\n\n",
    )

    print("-", missing_ids, end="\n\n")
    print("+", revised_ids)
