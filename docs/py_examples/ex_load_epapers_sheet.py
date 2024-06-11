from noltaSympoPubTools.sheet2json import load_epapers_sheet

session_list = load_epapers_sheet(
    filename="db_extract.csv",
    tz_offset_h=2,
)

session_list.dump_json(
    filename="data.json",
    verbose=True,
)
