from noltaSympoPubTools.json2metaCSV import load_sessions

sessions = load_sessions(
    data_json="data.json",
    ss_organizers_json="ss_organizers.json",
    common_json="common.json",
)

sessions.dump_csv(
    filename="metadata_session.csv",
    template="session_template.csv",
)
