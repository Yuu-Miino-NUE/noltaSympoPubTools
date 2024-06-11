from noltaSympoPubTools.sheet2json import load_session_sheet

session_sheet = load_session_sheet(
    input="db_extract.csv",
    tz_offset_h=2,
)

session_sheet.dump_json(
    filename="data.json",
    verbose=True,
)
