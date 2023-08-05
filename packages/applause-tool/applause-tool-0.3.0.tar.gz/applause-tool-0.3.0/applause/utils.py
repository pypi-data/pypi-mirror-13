import logging
import six
import click

from functools import wraps
from .session import AuthSession
from . import settings
from clint.textui.progress import Bar as ProgressBar


def enable_debug_mode():
    """
    Sets the log level to debug + enables verbose logging for HTTP calls.
    """
    try:
        import http.client as http_client
    except ImportError:
        # Python 2
        import httplib as http_client
    http_client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def get_emails(email_lists):
    email_lists = email_lists or []
    emails = []
    for email_text in email_lists:
        for line in email_text.splitlines():
            line = line.strip()
            if line:
                if not isinstance(line, six.text_type):
                    line = line.decode("utf8")
                emails.append(line)
    return emails


def create_progress_bar_callback(encoder):
    """
    This is a callback function for a multipart encoder, which renders a progress bar
    """
    encoder_len = encoder.len
    bar = ProgressBar(expected_size=encoder_len, filled_char='=')

    def callback(monitor):
        bar.show(monitor.bytes_read)
    return callback


def requires_login(command):
    """
    This is a decorator to methods representing CLI commands which require being authenticated.
    """
    @wraps(command)
    def func(*args, **kwargs):
        auth_session = AuthSession(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET)
        if not auth_session.is_active():
            raise click.UsageError("You must login before performing this action.")
        return command(auth_session, *args, **kwargs)
    return func
