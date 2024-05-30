import os, json
import pandas as pd
import numpy as np

from .models import ReviseItem, JsonEncoder, Session

__all__ = [
    "revise_csv2json",
    "get_revised_ids",
    "get_all_ids",
    "get_records_by_ids",
    "show_revise_summary",
]


def save_items(items: list[ReviseItem], output_json: str):
    """Save ReviseItem objects to a JSON file.

    Parameters
    ----------
    items : list[ReviseItem]
        List of ReviseItem objects.
    output_json : str
        Output JSON file path.
    """
    with open(output_json, "w") as f:
        json.dump(items, f, indent=4, ensure_ascii=False, cls=JsonEncoder)


def _load_err_msg_csv(input_csv: str):
    df = pd.read_csv(input_csv)
    df = df.replace(np.nan, None)  # convert NaN to None

    record_dicts = df.to_dict(orient="records")
    ret = {d["ERR_KEY"]: d["ERR_MSG"] for d in record_dicts}
    return ret


def revise_csv2json(input_csv: str, data_json: str, output_json: str, err_msg_csv: str):
    """Convert CSV data to JSON data for revision request.

    Parameters
    ----------
    input_csv : str
        Input CSV file path.
    data_json : str
        Data JSON file path.
    output_json : str
        Output JSON file path.
    err_msg_csv : str
        Error message CSV file path.

    Raises
    ------
    ValueError
        If a paper is not found in the data JSON file.
    """
    ERROR_MSG = _load_err_msg_csv(err_msg_csv)

    df = pd.read_csv(input_csv)
    df = df.replace(np.nan, None)  # convert NaN to None
    record_dicts = df.to_dict(orient="records")

    with open(data_json) as f:
        sessions = [Session(**s) for s in json.load(f)]

    revise_items = []
    for d in record_dicts:
        kwargs = {"pdfname": d["PDF_NAME"], "ext_msg": d["EXTRA_COMMENTS"]}

        # Load error data from CSV
        errors = []
        for k, v in d.items():
            if k in ERROR_MSG and v == 1:
                errors.append(ERROR_MSG[k])

        # Find paper in data JSON
        basename = d["PDF_NAME"].split(".")[0]
        code, order = basename[0:-1], int(basename[-1])
        try:
            idx = [s.code for s in sessions].index(code)
            idx2 = [p.order for p in sessions[idx].papers].index(order)
            kwargs |= {
                "paper_id": sessions[idx].papers[idx2].id,
                "title": sessions[idx].papers[idx2].title,
                "contact": sessions[idx].papers[idx2].contact,
            }
        except ValueError:
            raise ValueError(f"Paper not found in {data_json} for {d['PDF_NAME']}")

        kwargs["errors"] = errors

        try:
            revise_items.append(ReviseItem(**kwargs))
        except Exception as e:
            print(kwargs)
            raise e

    save_items(revise_items, output_json)


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
