import os, json
import pandas as pd
import numpy as np

from .models import ReviseItem, ReviseItemList, SessionList

__all__ = [
    "load_err_sheet",
    "load_revise_sheet",
    "get_ritems",
    "show_revise_summary",
]


def load_err_sheet(err_sheet: str) -> dict[str, str]:
    """Convert error sheet to dictionary.

    Parameters
    ----------
    err_sheet : str
        Input sheet file path. The sheet should have the columns 'ERR_KEY' and 'ERR_MSG',
        which are error keys and messages, respectively.
        File format should be CSV or Excel.

    Returns
    -------
    dict[str, str]
        Dictionary of error keys and messages.

    Examples
    --------
    The error sheet should have the following structure.

    .. literalinclude:: /py_examples/err_msg.csv
        :caption: err_msg.csv

    Here is an example of how to use the :func:`load_err_sheet` function.

    .. literalinclude:: /py_examples/ex_load_err_sheet.py

    Created dictionary will be used in :func:`load_revise_sheet`.

    See Also
    --------
    .ReviseItem: Data class for revision request
    .ReviseItemList: List of revision requests
    .SessionList: List of session information
    .load_revise_sheet: Convert CSV data to ReviseItemList
    """

    if err_sheet.endswith(".csv"):
        df = pd.read_csv(err_sheet)
    elif err_sheet.endswith(".xlsx"):
        df = pd.read_excel(err_sheet)
    else:
        raise ValueError("Input file should be a CSV or Excel file.")

    df = df.replace(np.nan, None)  # convert NaN to None
    record_dicts = df.to_dict(orient="records")
    ret = {d["ERR_KEY"]: d["ERR_MSG"] for d in record_dicts}
    return ret


def load_revise_sheet(
    revise_sheet: str,
    err_dict: dict[str, str],
    data_json: str,
    excel_sheet_name: str | None = None,
) -> ReviseItemList:
    """Convert spreadsheet data to ReviseItemList.

    Parameters
    ----------
    revise_sheet : str
        Input sheet file path. The sheet should have the columns 'PDF_NAME', 'EXTRA_COMMENTS', and error keys.
        File format should be CSV or Excel.
    err_dict : dict[str, str]
        Error message dictionary. The dictionary should have error keys as keys and error messages as values.
    data_json : str
        Data JSON file path. The JSON file should have the structure of :class:`.Session`.

    Returns
    -------
    ReviseItemList
        List of revision requests.

    Examples
    --------
    The revision sheet should have the following structure.

    .. literalinclude:: /py_examples/revise_sheet.csv
        :caption: revise_sheet.csv

    The data JSON file should have the structure of :class:`.Session`.

    .. literalinclude:: /py_examples/data_with_pages.json
        :caption: data.json
        :language: json

    Here is an example of how to use the :func:`load_revise_sheet` function.

    .. literalinclude:: /py_examples/ex_load_revise_sheet.py

    Refer to :func:`load_err_sheet` for creating the error dictionary.
    The script will output a JSON file with the following structure.

    .. literalinclude:: /py_examples/revise_items.json
        :caption: revise_items.json
        :language: json

    The created JSON file will be used in :func:`.compose_emails` or :func:`.send_email`.


    See Also
    --------
    .ReviseItem: Data class for revision request
    .ReviseItemList: List of revision requests
    .SessionList: List of session information
    .load_err_sheet: Convert error sheet to dictionary
    .compose_emails: Compose emails for revision requests
    .send_email: Send emails for revision requests
    """
    if revise_sheet.endswith(".csv"):
        df = pd.read_csv(revise_sheet)
    elif revise_sheet.endswith(".xlsx"):
        if excel_sheet_name is not None:
            df = pd.read_excel(revise_sheet, sheet_name=excel_sheet_name)
        else:
            df = pd.read_excel(revise_sheet)
    df = df.replace(np.nan, None)  # convert NaN to None
    record_dicts = df.to_dict(orient="records")

    with open(data_json) as f:
        sessions = SessionList(json.load(f))

    revise_items = ReviseItemList()
    for d in record_dicts:
        try:
            kwargs = {"pdf_name": d["PDF_NAME"]}
        except KeyError:
            raise ValueError(
                f"Columns 'PDF_NAME' and 'EXTRA_COMMENTS' are required in {revise_sheet}"
            )

        # Load error data
        kwargs["errors"] = []
        for k, v in d.items():
            if k in err_dict and v == 1:
                kwargs["errors"].append(err_dict[k])
            elif k == "EXTRA_COMMENTS":
                kwargs["extra_comments"] = v
            else:
                pass

        # Find paper in data JSON
        basename = kwargs["pdf_name"].split(".")[0]
        code, order = basename[0:-1], int(basename[-1])
        try:
            idx = [s.code for s in sessions].index(code)
            idx2 = [p.order for p in sessions[idx].papers].index(order)
            kwargs |= {
                k: getattr(sessions[idx].papers[idx2], k)
                for k in ["id", "title", "contact"]
            }
        except ValueError:
            raise ValueError(f"Paper not found in {data_json} for {kwargs['pdf_name']}")

        revise_items.append(ReviseItem(**kwargs))

    return revise_items


def _get_revised_ids(revised_pdfs_dir: str) -> set[int]:
    """Get the IDs of revised papers from the directory of revised PDFs.

    Parameters
    ----------
    revised_pdfs_dir : str
        Directory path containing revised PDFs. PDF file names should be the paper IDs, not including the session code.

    Returns
    -------
    set[int]
        Set of paper IDs.
    """
    revised_ids: set[int] = set()
    for _, _, files in os.walk(revised_pdfs_dir):
        for file in files:
            if file.endswith(".pdf"):
                revised_ids.add(int(file[:-4]))
    return revised_ids


def _get_all_pids(revise_json: str) -> set[int]:
    """Get all paper IDs from the JSON file.

    Parameters
    ----------
    revise_json : str
        Path to the JSON file.

    Returns
    -------
    set[str]
        Set of paper IDs.
    """
    all_ids: set[int] = set()
    with open(revise_json) as f:
        data = ReviseItemList(json.load(f))
        for item in data:
            all_ids.add(item.id)
    return all_ids


def get_ritems(revise_json: str, pids: set[int]) -> ReviseItemList:
    """Get a single or multiple ReviseItem records from the JSON file.

    Parameters
    ----------
    revise_json : str
        Path to the JSON file. The JSON file should have the structure of :class:`.ReviseItemList`.
    ids : set[int]
        Set of paper IDs.

    Returns
    -------
    ReviseItemList
        List of records.

    Examples
    --------
    Here is an example of how to use the :func:`get_ritems` function.

    .. literalinclude:: /py_examples/ex_get_ritems.py

    The function will return a single :class:`.ReviseItem` object for the paper ID 6000.

    See Also
    --------
    .ReviseItem: Data class for revision request
    .ReviseItemList: List of revision requests
    """
    with open(revise_json) as f:
        data = ReviseItemList(json.load(f))

    ret = ReviseItemList()
    for id in pids:
        try:
            idx = [item.id for item in data].index(id)
            ret.append(data[idx])
        except ValueError:
            raise ValueError(f"Paper ID {id} not found in the JSON file.")

    return ret


def show_revise_summary(revise_json: str, revised_pdfs_dir: str) -> dict[str, set[int]]:
    """Show the summary of revised papers.

    Parameters
    ----------
    revise_json : str
        Path to the JSON file. The JSON file should have the structure of :class:`.ReviseItemList`.
    revised_pdfs_dir : str
        Directory path containing revised PDFs. PDF file names should be the paper IDs.

    Returns
    -------
    dict[str, set[int]]
        Dictionary of paper IDs for all, missing, and revised papers.

    Examples
    --------
    Put the revised PDFs in the directory `revised_pdfs` and run the following script.

    .. literalinclude:: /py_examples/ex_show_revise_summary.py

    The script will print the summary of revised papers.

    .. code-block:: none

        # all= missing + revised (rate % revised)
        1 = 0 + 1 (100.00 % revised)

        Not Revised IDs:

        Revised IDs: 6000

    - First line shows the total number of papers, the number of missing papers, the number of revised papers, and the revision rate.
    - Second line shows the missing paper IDs.
    - Third line shows the revised paper IDs.

    See Also
    --------
    .ReviseItem: Data class for revision request
    .ReviseItemList: List of revision requests
    """

    all_ids = _get_all_pids(revise_json)
    revised_ids = _get_revised_ids(revised_pdfs_dir)
    missing_ids = all_ids - revised_ids

    rate = len(revised_ids) / len(all_ids) * 100
    print("# all= missing + revised (rate % revised)")
    print(
        len(all_ids),
        "=",
        len(missing_ids),
        "+",
        len(revised_ids),
        f"({rate:.2f} % revised)",
        end="\n\n",
    )

    print("Not Revised IDs:", *missing_ids, end="\n\n")
    print("Revised IDs:", *revised_ids)

    return {
        "all": all_ids,
        "missing": missing_ids,
        "revised": revised_ids,
    }
