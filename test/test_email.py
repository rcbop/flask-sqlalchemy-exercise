from unittest.mock import Mock, patch

import pytest

from api.email import render_template, send_email_from_postmaster


def test_send_email_from_postmaster_without_mailgun_cfg():
    """Test that send_email_from_postmaster() returns a requests.Response."""
    with pytest.raises(ValueError):
        send_email_from_postmaster(email="john@doe.com", username="john")

@patch("api.email.requests.post")
@patch("api.email.MAILGUN_DOMAIN", "test")
@patch("api.email.MAILGUN_TOKEN", "test")
def test_send_email_from_postmaster(request_post_mock: Mock):
    """Test that send_email_from_postmaster() returns a requests.Response."""
    username = "john"
    response = send_email_from_postmaster(
        email="john@doe.com",
        username=username)
    assert isinstance(response, Mock)
    request_post_mock.assert_called_once_with(
        url = "https://api.mailgun.net/v3/test.mailgun.org/messages",
        auth = ("api", "test"),
        data = {
            "from": "Rcbop <postmaster@test.mailgun.org>",
            "to": ["john@doe.com"],
            "subject": f"Welcome {username}! You have successfully registered to our Stores API.",
            "text": "Successfully created a new user.",
            "html": render_template("email/welcome.html", username=username)
        },
        timeout=5)
