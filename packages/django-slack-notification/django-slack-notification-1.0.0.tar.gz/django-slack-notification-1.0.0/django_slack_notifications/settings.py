from django.conf import settings


USER_SETTINGS = getattr(settings, 'SLACK_NOTIFICATIONS', {})
DEFAULT_SETTINGS = {
    'WEBHOOK_URL': None,
    'CHANNEL': None,
    'USERNAME': None,
    'ICON_EMOJI': None,
}

slack_settings = DEFAULT_SETTINGS
slack_settings.update(USER_SETTINGS)
