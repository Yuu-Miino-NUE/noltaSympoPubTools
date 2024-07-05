from noltaSympoPubTools.json2metaCSV import load_meta_articles

articles = load_meta_articles(
    data_json="data.json",
    award_json="awards.json",
)

articles.dump_csv(
    filename="metadata_article.csv",
    template="article_template.csv",
)
