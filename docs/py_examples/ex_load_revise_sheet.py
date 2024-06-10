from noltaSympoPubTools.requestRevise import err_sheet2dict, load_revise_sheet


err_dict = err_sheet2dict(err_sheet="err_msg.csv")

revise_items = load_revise_sheet(
    revise_sheet="revise_sheet.csv",
    err_dict=err_dict,
    data_json="data.json",
)

revise_items.dump_json(
    filename="revise_items.json",
    verbose=True,
)
