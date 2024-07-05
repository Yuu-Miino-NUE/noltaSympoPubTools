from noltaSympoPubTools.json2metaCSV import load_meta_common

common = load_meta_common(common_json="common.json")

common.dump_csv(
    filename="metadata_common.csv",
    template="common_template.csv",
)
