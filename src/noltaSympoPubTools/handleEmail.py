import json
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from logging import getLogger, config
import os
from dotenv import load_dotenv

from .models import ReviseItem, ReviseItemList, SMTPConfig

__all__ = [
    "send_email",
    "compose_emails",
    "save_emails",
]


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


def send_email(msg: MIMEText, dry_run: bool = True, dump: bool = True) -> bool:
    """Send email

    Parameters
    ----------
    msg : MIMEText
        Email message to send.
    dry_run : bool, optional
        If `True`, the email is not sent and only logged, by default `True`.
    dump : bool, optional
        If `True`, the email is saved to a file, by default `True`.
        Dumped emails are saved in the directory specified in the environment variable DUMP_DIR.


    .. attention::

        To send an email, you need to turn off the ``dry_run`` option.

    .. note::

        :func:`.send_email` supports sending emails using the SMTP server specified in the environment variables.
        Please set the following environment variables:

        ==================== ==============================
        Environment variable Description
        ==================== ==============================
        SMTP_SERVER          SMTP server address
        SMTP_PORT            SMTP server port
        SMTP_USER            SMTP username
        SMTP_USERNAME        SMTP username (for display)
        SMTP_PASSWORD        SMTP password (optional)
        ==================== ==============================

        :func:`.send_email` also logs the email message to the log file specified in the environment variable DUMP_DIR.
        Configuration for logging can be set in a JSON file and specified in the environment variable LOG_CONFIG.

        One will prepare a ``.env`` file with the following content:

        .. code-block:: shell

                SMTP_SERVER=smtp.example.com
                SMTP_PORT=587
                SMTP_USER=YOUR_EMAIL_ADDRESS
                SMTP_USERNAME=YOUR_NAME
                SMTP_PASSWORD=YOUR_PASSWORD
                DUMP_DIR=.log
                LOG_CONFIG=log_config.json

    Returns
    -------
    bool
        True if the email is sent successfully.

    Examples
    --------
    Firstly, prepare a ``.env`` file:

    .. code-block:: shell

        $ cat .env

        SMTP_SERVER=smtp.example.com
        SMTP_PORT=587
        SMTP_USER=YOUR_EMAIL_ADDRESS
        SMTP_USERNAME=YOUR_NAME
        SMTP_PASSWORD=YOUR_PASSWORD
        DUMP_DIR=.log
        LOG_CONFIG=log_config.json

    Then, run a Python script to send an email:

    .. literalinclude:: /py_examples/ex_send_email.py

    See Also
    --------
    .ReviseItem: Data class for revise item.
    compose_emails: Compose emails from JSON data and template file.

    """
    load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

    # Set up logging
    if (log_config_file := os.getenv("LOG_CONFIG")) is not None:
        try:
            with open(os.path.join(os.getcwd(), log_config_file), "r") as f:
                log_conf = json.load(f)
            config.dictConfig(log_conf)

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Specified log config file not found: {log_config_file}"
            )

    logger = getLogger("email_logger")
    dump_dir = os.getenv("DUMP_DIR") or ".log"

    try:
        CONFIG = _load_config()
        _msg = msg
        _msg["From"] = formataddr((CONFIG.SMTP_USERNAME, CONFIG.SMTP_USER))
        _msg["Bcc"] = CONFIG.SMTP_USER

        s = smtplib.SMTP(CONFIG.SMTP_SERVER, CONFIG.SMTP_PORT)
        s.ehlo()
        s.starttls()
        s.ehlo()
        if CONFIG.SMTP_PASSWORD is not None:
            s.login(CONFIG.SMTP_USER, CONFIG.SMTP_PASSWORD)
        if not dry_run:
            s.send_message(msg=_msg)
        s.close()

        logger.info(
            f"send_mail{' (dry_run)' if dry_run else ''}: {_msg['From']} -> {_msg['To']}: {_msg['Subject']}"
        )
        if dump:
            os.makedirs(dump_dir, exist_ok=True)
            with open(os.path.join(dump_dir, "email.dump"), "a") as f:
                f.write(_msg.as_string() + "\n")
        return True
    except Exception as e:
        logger.error(e)
        if dump:
            os.makedirs(dump_dir, exist_ok=True)
            with open(os.path.join(dump_dir, "failed_email.dump"), "a") as f:
                f.write(msg.as_string() + "\n")
        return False


def _make_email(to_addr: str, subject: str, body: str) -> MIMEText:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["To"] = to_addr
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


def compose_emails(
    revise_json: str, subject: str, template_file: str
) -> list[MIMEText]:
    """Compose emails from JSON data and template file.

    Parameters
    ----------
    revise_json : str
        Path to the input JSON file. The JSON file should have the structure of :class:`.ReviseItem`.
    subject : str
        Subject line of the email. The string should contain a placeholder ``{id}``.
    template_file : str
        Path to the email template file. The template should contain placeholders ``{name}``, ``{title}``, and ``{errors}``,
        which will be replaced by the name of the contact person, the title of the paper, and the list of errors, respectively.

    Returns
    -------
    list[MIMEText]
        List of MIMEText objects.

    Raises
    ------
    ValueError
        If email address is not found.

    Note
    ----
    The :func:`compose_emails` function only composes emails and does not send them.
    To send emails, use the :func:`send_email` function.

    Examples
    --------
    Prepare a template file like the following:

    .. literalinclude:: /py_examples/email_templates/initial_contact.txt
        :language: text

    Here is an example of how to use the :func:`compose_emails` function.

    .. literalinclude:: /py_examples/ex_compose_emails.py


    See Also
    --------
    .ReviseItem: Data class for revise item.
    save_emails: Save emails as text files.
    send_email: Send email.
    """
    with open(revise_json) as f:
        data = [ReviseItem(**r) for r in json.load(f)]

    with open(template_file) as f:
        template = f.read()

    emails: list[MIMEText] = []
    for d in data:
        if d.contact.email is None:
            raise ValueError(f"Email address not found for {d.contact.name}")

        body = _make_body(d.contact.name, d.title, d.errors, d.extra_comments, template)
        email = _make_email(d.contact.email, subject.format(id=d.id), body)
        emails.append(email)
    return emails


def save_emails(revise_json: str, msgs: list[MIMEText], out_dir: str = "") -> None:
    """Save emails as text files.

    Parameters
    ----------
    revise_json : str
        Path to the input JSON file. The JSON file should have the structure of :class:`.ReviseItem`.
    msgs : list[MIMEText]
        List of MIMEText objects.
    out_dir : str, optional
        Output directory path. If not specified, the current directory is used.

    Examples
    --------
    Here is an example of how to use the :func:`save_emails` function.

    .. literalinclude:: /py_examples/ex_save_emails.py

    See Also
    --------
    .ReviseItem: Data class for revise item.
    compose_emails: Compose emails from JSON data and template file.
    """
    try:
        with open(revise_json) as f:
            data = ReviseItemList(json.load(f))
    except FileNotFoundError:
        raise FileNotFoundError(f"Input JSON file not found: {revise_json}")

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    try:
        for d, m in zip(data, msgs):
            with open(os.path.join(out_dir, str(d.id) + ".txt"), "w") as f:
                f.write(m.as_string())
    except FileNotFoundError:
        raise FileNotFoundError(f"Output directory not found: {out_dir}")
    except Exception as e:
        raise e
