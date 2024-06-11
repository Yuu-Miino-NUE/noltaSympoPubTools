from noltaSympoPubTools.sheet2json import update_sessions

updated_sessions = update_sessions(
    data_json="data.json",
    update_json="update.json",
)

updated_sessions.dump_json(
    "updated_data.json",
    verbose=True,
)
