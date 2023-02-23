from unittest.mock import Mock, patch
from api.resources.user import send_email_from_postmaster


@patch("api.email.requests.post")
@patch("api.email.MAILGUN_DOMAIN", "test")
@patch("api.email.MAILGUN_TOKEN", "test")
def test_send_email_from_postmaster(request_post_mock: Mock):
    """Test that send_email_from_postmaster() returns a requests.Response."""
    response = send_email_from_postmaster(
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