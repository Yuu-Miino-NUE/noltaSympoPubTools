from noltaSympoPubTools.handleEmail import compose_emails, send_email

emails = compose_emails(
    input_json="revise_items.json",
    subject="Revision request for paper {id}",
    template_file="template.txt",
)

for email in emails:
    send_email(
        msg=email,
        dry_run=False,
        dump=True,
        load_env=True,
    )
