from noltaSympoPubTools.json2metaCSV import load_articles

articles = load_articles(data_json="data.json", award_json="award.json")

articles.dump_csv(
    filename="metadata_article.csv",
    template="article_template.csv",
)
