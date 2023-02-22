from unittest.mock import Mock, patch

import api.resources.user
from api.resources.user import EmailSender


@patch("api.resources.user.requests.post")
@patch("api.resources.user.MAILGUN_DOMAIN", "test")
@patch("api.resources.user.MAILGUN_TOKEN", "test")
def test_send_email_from_postmaster(request_post_mock: Mock):
    """Test that send_email_from_postmaster() returns a requests.Response."""
    response = EmailSender.send_email_from_postmaster(
        mail_to="john@doe.com",
        subject="Test",
        body="Test")
    assert isinstance(response, Mock)
    request_post_mock.assert_called_once_with(
        url="https://api.mailgun.net/v3/test.mailgun.org/messages",
        auth=("api", "test"),
        data={
            "from": "Mailgun <postmaster@test.mailgun.org>",
            "to": "john@doe.com",
            "subject": "Test",
            "text": "Test"
        })