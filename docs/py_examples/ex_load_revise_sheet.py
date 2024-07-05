from noltaSympoPubTools.requestRevise import load_err_sheet, load_revise_sheet


err_dict = load_err_sheet(err_sheet="err_msg.csv")

revise_items = load_revise_sheet(
    revise_sheet="revise_sheet.csv",
    err_dict=err_dict,
    data_json="data.json",
)

revise_items.dump_json(
    filename="revise_items.json",
    verbose=True,
)
