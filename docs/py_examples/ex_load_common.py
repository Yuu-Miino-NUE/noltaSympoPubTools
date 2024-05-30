from noltaSympoPubTools.json2metaCSV import load_common

common = load_common(common_json="common_json")

common.dump_csv(
    filename="metadata_common.csv",
    template="common_template.csv",
)
