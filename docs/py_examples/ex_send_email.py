from noltaSympoPubTools.handleEmail import compose_emails, send_email

emails = compose_emails(
    revise_json="revise_items.json",
    subject="Revision request for paper {id}",
    template_file="email_templates/initial_contact.txt",
)

for email in emails:
    send_email(
        msg=email,
        dry_run=True,  # Set to False to send the email
        dump=True,
    )
