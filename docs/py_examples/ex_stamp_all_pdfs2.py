from noltaSympoPubTools.pdfTools import stamp_all_pdfs

page_added_data = stamp_all_pdfs(
    data_json="data.json",
    first_page_overlay="first_page_overlay.pdf",
    input_pdfs_dir="row_pdfs",
    output_pdfs_dir="stamped_pdfs",
    verbose=True,
    overwrite_json=True,
)
