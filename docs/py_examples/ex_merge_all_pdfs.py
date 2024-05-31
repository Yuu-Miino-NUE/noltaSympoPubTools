from noltaSympoPubTools.pdfTools import merge_all_pdfs

merge_all_pdfs(
    data_json="data.json",
    input_pdf_dir="stamped_pdfs",
    output_pdf="merged.pdf",
    verbose=True,
)
