from noltaSympoPubTools.json2metaCSV import json2meta_sessions

meta_sessions = json2meta_sessions(
    data_json="data.json",
    ss_organizers_json="ss_organizers.json",
    common_json="common.json",
)

meta_sessions.dump_csv(
    filename="metadata_session.csv",
    template="session_template.csv",
)
