from django.conf import settings


DEFAULT_SETTINGS = {
    'PATH': '/heartbeat',
    'RETURN_CODE': 503,
    'CACHE_HEALTH': False,
    'DATABASE_READ_HEALTH': True,
    'DATABASE_WRITE_HEALTH': False
}

PULSEWARE_DEFAULT_SETTINGS = getattr(settings, 'PULSEWARE_DEFAULT_SETTINGS', {})
for key in DEFAULT_SETTINGS:
    if key not in PULSEWARE_DEFAULT_SETTINGS:
        PULSEWARE_DEFAULT_SETTINGS[key] = DEFAULT_SETTINGS[key]
