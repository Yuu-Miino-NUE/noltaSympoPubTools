from noltaSympoPubTools.pdfTools import stamp_single_pdf

pages = stamp_single_pdf(
    input_pdf="row_pdfs/6000.pdf",
    output_pdf="stamped_pdfs/A2L-21.pdf",
    first_page_overlay="first_page_overlay.pdf",
)

print(pages)
# Expected output: [1, 1]
