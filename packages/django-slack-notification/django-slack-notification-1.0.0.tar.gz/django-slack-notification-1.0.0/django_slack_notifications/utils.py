import json

import requests

from django.core.exceptions import ImproperlyConfigured

from django_slack_notifications.settings import slack_settings


if not slack_settings['WEBHOOK_URL']:
    raise ImproperlyConfigured("WEBHOOK_URL is required. You sould set WEBHOOK_URL in django settings.")


def send_text(*args, **kwargs):
    channel = kwargs.get('channel', slack_settings['CHANNEL'])
    username = kwargs.get('username', slack_settings['USERNAME'])
    icon_emoji= kwargs.get('icon_emoji', slack_settings['ICON_EMOJI'])
    text = kwargs.get('text', "Default message.")

    payload = {
        "channel": channel,
        "username": username,
        "text": text,
        "icon_emoji": icon_emoji,
    }
    payload = json.dumps(payload)
    response = requests.post(slack_settings['WEBHOOK_URL'], payload)

    return response
