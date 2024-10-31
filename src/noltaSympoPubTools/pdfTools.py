"""PDF tools for stamping logos and texts, and merging.

.. _PdfStampTools: https://github.com/Yuu-Miino-NUE/PdfStampTools

This module depends on the PdfStampTools_.

.. _note_fpo:

Note
----

For stamping logos and texts, an overlay PDF file is required.
PdfStampTools_ provides a function to create the overlay.

.. literalinclude:: /py_examples/ex_put_logo_with_text.py

Here is an example of how to create the overlay.
The output PDF file will include the logo and the symposium title in the margin area, as shown in the image.

.. image:: /_images/first_page_overlay.png
    :class: with-border
    :width: 50%
    :align: center

"""

import json, os
from pypdf import PdfWriter

from PdfStampTools import stamp_pdf, NumberEnclosure
from .models import SessionList

__all__ = ["stamp_all_pdfs", "stamp_single_pdf", "merge_all_pdfs"]


def stamp_all_pdfs(
    data_json: str,
    first_page_overlay: str,
    input_pdfs_dir: str,
    output_pdfs_dir: str,
    encl: NumberEnclosure = "en_dash",
    verbose: bool = False,
    overwrite_json: bool = False,
) -> SessionList:
    """Stamp overlays and page numbers on all PDFs in the input directory according to the data JSON.

    Parameters
    ----------
    data_json : str
        Path to the data JSON file. The JSON file should have the structure of :class:`.Session`.
    first_page_overlay : str
        Path to the overlay PDF file for the first page.
        If the pdf file has multiple pages, only the first page will be used.
        The overlay will only have the logo and the symposium title in the margin area.
        Refer to :ref:`note on first page overlay <note_fpo>` for more details.
    input_pdfs_dir : str
        Path to the input PDF directory. The PDF files should be named as ``{paper_id}.pdf``.
    output_pdfs_dir : str
        Path to the output PDF directory. The stamped PDF files will be saved in this directory.
        The filenames will be ``{session_code}{paper_order}.pdf``.
    encl : NumberEnclosure, optional
        .. _enclosures:

        Page number enclosure, by default ``"en_dash"``.
        The following options are available:

        ============= ==========================
        encl          Enclosure with page number
        ============= ==========================
        ``"parens"``  ( 1 )
        ``"en_dash"`` – 1 –
        ``"em_dash"`` — 1 —
        ``"minus"``   − 1 −
        ``"page"``    p. 1
        ``"Page"``    P. 1
        ============= ==========================

    verbose : bool, optional
        Whether to print the progress, by default False.

    overwrite_json : bool, optional
        Whether to overwrite the input JSON file with the updated data, by default False.

    Returns
    -------
    SessionList
        :class:`.SessionList` object, containing the updated data.
        The page numbers of the papers will be updated.

    Examples
    --------
    Here is an example of how to stamp all PDFs in the input directory.

    .. literalinclude:: /py_examples/ex_stamp_all_pdfs.py

    The following image shows the original and stamped PDFs.

    .. image:: /_images/ex_stamp.png
        :class: with-border
        :width: 100%
        :align: center

    Using :meth:`.SessionList.dump_json`, the updated data can be saved to the JSON file.

    .. literalinclude:: /py_examples/pages.diff
        :caption: diff between ``data.json`` and ``data_with_pages.json.json``

    See Also
    --------
    .stamp_single_pdf: Stamp a single PDF file with the overlay.
    """
    with open(data_json, "r") as f:
        data = SessionList(json.load(f))

    with open(first_page_overlay, "rb") as f:
        page_start = 1
        for session in data:
            for p in [s for s in session.papers if not s.plenary]:
                page_start_next = stamp_pdf(
                    input=os.path.join(input_pdfs_dir, f"{str(p.id)}.pdf"),
                    output=os.path.join(
                        output_pdfs_dir, f"{session.code+str(p.order)}.pdf"
                    ),
                    first_page_overlay=f,
                    encl=encl,
                    start_num=page_start,
                )
                p.pages = (page_start, page_start_next - 1)
                page_start = page_start_next
                if verbose:
                    print("Proceeded: pp.", p.pages)

    if overwrite_json:
        data.dump_json(data_json)

    return data


def stamp_single_pdf(
    input_pdf: str,
    output_pdf: str,
    first_page_overlay: str,
    encl: NumberEnclosure = "en_dash",
    page_start: int = 1,
) -> tuple[int, int]:
    """Stamp a single PDF file with the overlay.

    Parameters
    ----------
    input_pdf : str
        Path to the input PDF file.
    output_pdf : str
        Path to the output PDF file.
    first_page_overlay : str
        Path to the overlay PDF file for the first page.
        The overlay will only have the logo and the symposium title in the margin area.
        Refer to :ref:`note on first page overlay <note_fpo>` for more details.
    encl : NumberEnclosure, optional
        Number enclosure type, by default "en_dash".
        See :ref:`encl <enclosures>` of :func:`.stamp_all_pdfs` for more details.
    page_start : int, optional
        Starting page number, by default 1.

    Returns
    -------
    list[int]
        List of two integers, representing the start and end page numbers.

    Examples
    --------
    Here is an example of how to stamp a single PDF file.

    .. literalinclude:: /py_examples/ex_stamp_single_pdf.py

    See Also
    --------
    .stamp_all_pdfs: Stamp overlays and page numbers on all PDFs in the input directory according to the data JSON.
    """
    with open(first_page_overlay, "rb") as f:
        page_start_next = stamp_pdf(
            input=input_pdf,
            output=output_pdf,
            first_page_overlay=f,
            encl=encl,
            start_num=page_start,
        )
        return (page_start, page_start_next - 1)


def merge_all_pdfs(
    data_json: str,
    input_pdf_dir: str,
    output_pdf: str,
    verbose: bool = False,
):
    """Merge all PDFs in the input directory according to the data JSON.

    Parameters
    ----------
    data_json : str
        Path to the data JSON file. The JSON file should have the structure of :class:`.Session`.
        The order of the PDFs will be determined by the order of the papers in the JSON file.
    input_pdf_dir : str
        Path to the input PDF directory. The PDF files should be named as ``{session_code}{paper_order}.pdf``.
    output_filename : str
        Filename of the merged PDF file.
    verbose : bool, optional
        Whether to print the progress, by default False.

    Examples
    --------
    Here is an example of how to merge all PDFs in the input directory.

    .. literalinclude:: /py_examples/ex_merge_all_pdfs.py
    """
    with open(data_json, "r") as f:
        data = SessionList(json.load(f))

    merger = PdfWriter()
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
