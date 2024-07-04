from noltaSympoPubTools.handleEmail import compose_emails

emails = compose_emails(
    revise_json="revise_items.json",
    subject="Revision request for paper {id}",
    template_file="email_templates/initial_contact.txt",
)
