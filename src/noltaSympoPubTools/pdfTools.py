import json, os
from pypdf import PdfMerger

from PdfStampTools import stamp_pdf, NumberEnclosure, put_logo_with_text, mm, cm
from .models import Session

__all__ = [
    "stamp_logo_and_pages",
    "stamp_single",
    "merge_all_pdfs_in_dir",
    "put_logo_with_text",
    "mm",
    "cm",
]


def stamp_logo_and_pages(
    data_json: str,
    first_page_overlay: str,
    input_pdf_dir: str,
    output_pdf_dir: str,
    encl: NumberEnclosure = "en_dash",
    verbose: bool = False,
) -> list[Session]:
    """Stamp the first page with the logo and the rest of the pages with the page numbers.

    Parameters
    ----------
    data_json : str
        Path to the data JSON file.
    first_page_overlay : str
        Path to the overlay PDF file for the first page.
    input_pdf_dir : str
        Path to the input PDF directory.
    output_pdf_dir : str
        Path to the output PDF directory.
    encl : NumberEnclosure, optional
        Number enclosure type, by default "en_dash".
    verbose : bool, optional
        Whether to print the progress, by default False.

    Returns
    -------
    list[Session]
        List of Session objects.
    """
    with open(data_json, "r") as f:
        data = [Session(**s) for s in json.load(f)]

    with open(first_page_overlay, "rb") as f:
        page_start = 1
        for session in data:
            for p in [s for s in session.papers if not s.plenary]:
                page_start_next = stamp_pdf(
                    input=os.path.join(input_pdf_dir, f"{str(p.id)}.pdf"),
                    output=os.path.join(
                        output_pdf_dir, f"{session.code+str(p.order)}.pdf"
                    ),
                    first_page_overlay=f,
                    encl=encl,
                    start_num=page_start,
                )
                p.pages = (page_start, page_start_next - 1)
                page_start = page_start_next
                if verbose:
                    print("Proceeded: pp.", p.pages)

    return data


def stamp_single(
    input_pdf: str,
    output_pdf: str,
    first_page_overlay: str,
    encl: NumberEnclosure = "en_dash",
    page_start: int = 1,
):
    """Stamp a single PDF file with the overlay.

    Parameters
    ----------
    input_pdf : str
        Path to the input PDF file.
    output_pdf : str
        Path to the output PDF file.
    first_page_overlay : str
        Path to the overlay PDF file for the first page.
    encl : NumberEnclosure, optional
        Number enclosure type, by default "en_dash".
    page_start : int, optional
        Starting page number, by default 1.

    Returns
    -------
    _type_
        _description_
    """
    with open(first_page_overlay, "rb") as f:
        page_start_next = stamp_pdf(
            input=input_pdf,
            output=output_pdf,
            first_page_overlay=f,
            encl=encl,
            start_num=page_start,
        )
        return [page_start, page_start_next - 1]


def merge_all_pdfs_in_dir(
    data_json: str,
    input_pdf_dir: str,
    output_pdf: str,
    verbose: bool = False,
):
    """Merge all PDFs in the input directory according to the data JSON.

    Parameters
    ----------
    data_json : str
        Path to the data JSON file.
    input_pdf_dir : str
        Path to the input PDF directory.
    output_pdf : str
        Path to the output PDF file.
    verbose : bool, optional
        Whether to print the progress, by default False.
    """
    with open(data_json, "r") as f:
        data = [Session(**s) for s in json.load(f)]

    merger = PdfMerger()
    for session in data:
        for p in [s for s in session.papers if not s.plenary]:
            fname = os.path.join(input_pdf_dir, f"{session.code+str(p.order)}.pdf")

            if verbose:
                print("Loading:", fname, end="\r")

            merger.append(fname)

    if verbose:
        print("\nMerging...")

    merger.write(output_pdf)
    merger.close()

    if verbose:
        print("Done.")
