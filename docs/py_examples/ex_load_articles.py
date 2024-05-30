from noltaSympoPubTools.json2metaCSV import load_articles, save_data_as_csv

papers = load_articles(data_json="data.json", award_json="award.json")

save_data_as_csv(
    filename="metadata_article.csv",
    data=papers,
    template="article_template.csv",
)
