import os
import requests

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_TOKEN = os.getenv("MAILGUN_TOKEN")

def send_email_from_postmaster(subject: str, body: str, mail_to: str) -> requests.Response:
    """Send an email using Mailgun.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        mail_to (str): The recipient of the email.

    Raises:
        ValueError: If MAILGUN_DOMAIN or MAILGUN_TOKEN are not set.

    Returns:
        requests.Response: The response from Mailgun.
    """
    return send_email(
        subject=subject,
        body=body,
        mail_from=f"Mailgun <postmaster@{MAILGUN_DOMAIN}.mailgun.org>",
        mail_to=mail_to)

@staticmethod
def send_email(subject: str, body: str, mail_from: str, mail_to: str) -> requests.Response:
    """Send an email using Mailgun.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        mail_from (str): The sender of the email.
        mail_to (str): The recipient of the email.

    Raises:
        ValueError: If MAILGUN_DOMAIN or MAILGUN_TOKEN are not set.

    Returns:
        requests.Response: The response from Mailgun.
    """
    if MAILGUN_DOMAIN is None or MAILGUN_TOKEN is None:
        raise ValueError("MAILGUN_DOMAIN and MAILGUN_TOKEN must be set")

    return requests.post(
        url=f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}.mailgun.org/messages",
        auth=("api", MAILGUN_TOKEN),
        data={
            "from": mail_from,
            "to": mail_to,
            "subject": subject,
            "text": body
        })
