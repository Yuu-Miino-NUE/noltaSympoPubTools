from noltaSympoPubTools.handleEmail import compose_emails

emails = compose_emails(
    input_json="revise_items.json",
    subject="Revision request for paper {id}",
    template_file="template.txt",
)
