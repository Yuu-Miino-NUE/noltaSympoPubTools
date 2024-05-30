from noltaSympoPubTools.json2metaCSV import load_common, save_data_as_csv

common = load_common(common_json="common_json")

save_data_as_csv(
    filename="metadata_common.csv",
    data=[common],
    template="common_template.csv",
)
