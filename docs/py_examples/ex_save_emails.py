from noltaSympoPubTools.handleEmail import compose_emails, save_emails

emails = compose_emails(
    input_json="revise_items.json",
    subject="Revision request for paper {id}",
    template_file="template.txt",
)

save_emails(
    input_json="revise_items.json",
    msgs=emails,
    out_dir="emails",
)
