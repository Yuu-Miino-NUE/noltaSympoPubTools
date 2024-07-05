from noltaSympoPubTools.requestRevise import get_ritems, show_revise_summary

paper_ids = show_revise_summary(
    revise_json="revise_items.json",
    revised_pdfs_dir="revised_pdfs",
)

missing_items = get_ritems(
    revise_json="revise_items.json",
    pids=paper_ids["missing"],
)

missing_items.dump_json(
    filename="missing_items.json",
)
