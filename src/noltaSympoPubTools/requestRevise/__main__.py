from pydantic import BaseModel
import pandas as pd, numpy as np, json
from .. import Person, Session


class ReviseItem(BaseModel):
    pdfname: str
    errors: list[str]
    ext_msg: str | None
    paper_id: int
    title: str
    contact: Person


class _JsonEncoder(json.JSONEncoder):
    """JSON encoder for IterItems object."""

    def default(self, obj):
        if isinstance(obj, (Person, ReviseItem)):
            return dict(obj)
        return super().default(obj)


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
        json.dump(items, f, indent=4, ensure_ascii=False, cls=_JsonEncoder)


def _load_err_msg_csv(input_csv: str):
    df = pd.read_csv(input_csv)
    df = df.replace(np.nan, None)  # convert NaN to None

    record_dicts = df.to_dict(orient="records")
    ret = {d["ERR_KEY"]: d["ERR_MSG"] for d in record_dicts}
    return ret


def csv2json(input_csv: str, data_json: str, output_json: str, err_msg_csv: str):
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
