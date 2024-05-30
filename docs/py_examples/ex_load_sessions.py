from noltaSympoPubTools.json2metaCSV import load_sessions, save_data_as_csv

sessions = load_sessions(
    data_json="data.json",
    ss_organizers_json="ss_organizers.json",
    common_json="common.json",
)

save_data_as_csv(
    filename="metadata_session.csv",
    data=sessions,
    template="session_template.csv",
)
