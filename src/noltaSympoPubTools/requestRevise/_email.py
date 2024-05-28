import json
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from logging import getLogger, config
import os
from dotenv import load_dotenv

from . import ReviseItem

__all__ = [
    "send_email",
    "compose_emails",
    "save_emails",
]

# Load environment variables
load_dotenv()

# Set up logging
if (log_config_file := os.getenv("LOG_CONFIG")) is not None:
    try:
        with open(log_config_file, "r") as f:
            log_conf = json.load(f)
        config.dictConfig(log_conf)

    except FileNotFoundError:
        raise FileNotFoundError(f"Log config file not found: {log_config_file}")

logger = getLogger(__name__)
log_dir = os.getenv("LOG_DIR") or ".log"


class SMTPConfig:
    def __init__(
        self,
        SMTP_SERVER: str,
        SMTP_PORT: int,
        SMTP_USER: str,
        SMTP_USERNAME: str,
        SMTP_PASSWORD: str | None = None,
    ) -> None:
        self.SMTP_SERVER = SMTP_SERVER
        self.SMTP_PORT = SMTP_PORT
        self.SMTP_USER = SMTP_USER
        self.SMTP_USERNAME = SMTP_USERNAME
        self.SMTP_PASSWORD = SMTP_PASSWORD


def _load_config() -> SMTPConfig:
    mandatory_keys = ["SMTP_SERVER", "SMTP_PORT", "SMTP_USER", "SMTP_USERNAME"]
    optional_keys = ["SMTP_PASSWORD"]
    d = {}

    for key in mandatory_keys:
        if os.getenv(key) is None:
            raise ValueError(f"Environment variable {key} is not set.")
        d[key] = os.getenv(key)

    for key in optional_keys:
        d[key] = os.getenv(key)

    return SMTPConfig(**d)


def send_email(msg: MIMEText, dry_run=True, dump=True) -> bool:
    """Send email

    Parameters
    ----------
    msg : MIMEText
        Email message.
    dry_run : bool, optional
        If True, the email is not sent, by default True
    dump : bool, optional
        If True, the email is saved to a file, by default True

    Returns
    -------
    bool
        True if the email is sent successfully.

    Notes
    -----
    ``send_email`` uses the SMTP server specified in the environment variables.
    Please set the following environment variables:

    - SMTP_SERVER: SMTP server address
    - SMTP_PORT: SMTP server port
    - SMTP_USER: SMTP username
    - SMTP_USERNAME: SMTP username (for display)
    - SMTP_PASSWORD: SMTP password (optional)

    ``send_email`` also logs the email message to the log file specified in the environment variable LOG_DIR.
    Configuration for logging can be set in a JSON file and specified in the environment variable LOG_CONFIG.
    """
    try:
        CONFIG = _load_config()
        s = smtplib.SMTP(CONFIG.SMTP_SERVER, CONFIG.SMTP_PORT)
        s.ehlo()
        s.starttls()
        s.ehlo()
        if CONFIG.SMTP_PASSWORD is not None:
            s.login(CONFIG.SMTP_USER, CONFIG.SMTP_PASSWORD)
        if not dry_run:
            s.send_message(msg=msg)
        s.close()

        logger.info(
            f"send_mail{' (dry_run)' if dry_run else ''}: {msg['From']} -> {msg['To']}: {msg['Subject']}"
        )
        if dump:
            with open(log_dir + "email.dump", "a") as f:
                f.write(msg.as_string() + "\n")
        return True
    except Exception as e:
        logger.error(e)
        if dump:
            with open(log_dir + "failed_email.dump", "a") as f:
                f.write(msg.as_string() + "\n")
        return False


def _make_email(to_addr: str, subject: str, body: str) -> MIMEText:
    CONFIG = _load_config()
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = formataddr((CONFIG.SMTP_USERNAME, CONFIG.SMTP_USER))
    msg["To"] = to_addr
    msg["Bcc"] = CONFIG.SMTP_USER
    return msg


def _make_body(
    name: str, title: str, errors: list[str], ext_msg: str | None, template: str
) -> str:
    if ext_msg is None:
        ext_msg = ""
    else:
        ext_msg = f"\n\nHint message from committee: {ext_msg}"

    # Text replacement
    body = template.format(
        name=name,
        title=title,
        errors="\n".join([f"{i+1}. " + e for i, e in enumerate(errors)]) + ext_msg,
    )
    return body


def compose_emails(input_json: str, subject: str, template_file: str) -> list[MIMEText]:
    """Compose emails from JSON data and template file

    Parameters
    ----------
    input_json : str
        Path to the input JSON file.
    subject : str
        Subject line of the email. The string should contain a placeholder {id}.
    template_file : str
        Path to the email template file.

    Returns
    -------
    list[MIMEText]
        List of MIMEText objects.

    Raises
    ------
    ValueError
        If email address is not found.
    """
    with open(input_json) as f:
        data = [ReviseItem(**r) for r in json.load(f)]

    with open(template_file, "r") as f:
        template = f.read()

    emails = []
    for d in data:
        if d.contact.email is None:
            raise ValueError(f"Email address not found for {d.contact.name}")

        body = _make_body(d.contact.name, d.title, d.errors, d.ext_msg, template)
        email = _make_email(d.contact.email, subject.format(id=d.paper_id), body)
        emails.append(email)
    return emails


def save_emails(input_json: str, msgs: list[MIMEText], dir: str = "") -> None:
    """Save emails as text files.

    Parameters
    ----------
    input_json : str
        Path to the input JSON file.
    msgs : list[MIMEText]
        List of MIMEText objects.
    dir : str, optional
        Output directory path. If not specified, the current directory is used.
    """
    with open(input_json) as f:
        data = [ReviseItem(**r) for r in json.load(f)]

    if not os.path.exists(dir):
        os.mkdir(dir)

    for d, m in zip(data, msgs):
        with open(os.path.join(dir, str(d.paper_id) + ".txt"), "w") as f:
            f.write(m.as_string())
