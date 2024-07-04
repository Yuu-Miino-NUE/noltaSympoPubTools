from noltaSympoPubTools.handleEmail import compose_emails, save_emails

emails = compose_emails(
    revise_json="revise_items.json",
    subject="Revision request for paper {id}",
    template_file="email_templates/initial_contact.txt",
)

save_emails(
    revise_json="revise_items.json",
    msgs=emails,
    out_dir="emails",
)
