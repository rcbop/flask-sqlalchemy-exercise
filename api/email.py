"""send email module"""
import os
import requests
import jinja2

template_loader = jinja2.FileSystemLoader(searchpath="templates")
template_env = jinja2.Environment(loader=template_loader, autoescape=True)

def render_template(template_name: str, **kwargs) -> str:
    """Render a template.

    Args:
        template_name (str): The name of the template to render.

    Returns:
        str: The rendered template.
    """
    template = template_env.get_template(template_name)
    return template.render(**kwargs)

MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_TOKEN = os.getenv("MAILGUN_TOKEN")

def send_email_from_postmaster(email:str, username: str) -> requests.Response:
    """Send an email from postmaster.

    Args:
        email (str): destination email
        username (str): destination username

    Returns:
        requests.Response: Mailgun response
    """
    return send_email(
        subject=f"Welcome {username}! You have successfully registered to our Stores API.",
        body="Successfully created a new user.",
        mail_from=f"Rcbop <postmaster@{MAILGUN_DOMAIN}.mailgun.org>",
        mail_to=email,
        html=render_template("email/welcome.html", username=username))

def send_email(subject: str, body: str, mail_from: str, mail_to: str,
               html: str) -> requests.Response:
    """Send an email using mailgun.

    Args:
        subject (str): email subject
        body (str): email body
        mail_from (str): email sender
        mail_to (str): email recipient
        html (str): html body

    Raises:
        ValueError: MAILGUN_DOMAIN and MAILGUN_TOKEN must be set

    Returns:
        requests.Response: Mailgun response
    """
    if MAILGUN_DOMAIN is None or MAILGUN_TOKEN is None:
        raise ValueError("MAILGUN_DOMAIN and MAILGUN_TOKEN must be set")

    return requests.post(
        url=f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}.mailgun.org/messages",
        auth=("api", MAILGUN_TOKEN),
        data={
            "from": mail_from,
            "to": [mail_to],
            "subject": subject,
            "text": body,
            "html": html
        }, timeout=5)
