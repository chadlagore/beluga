import os

# Geo config (this is an odd place to put this isnt it).
VANCOUVER_LAT = 49.241
VANCOUVER_LON = -123.1073
VANCOUVER_RAD = "10km"

# Celery eats this stuff automagically.
timezone = 'America/Vancouver'
result_backend = os.environ['CELERY_RESULT_BACKEND']
CELERY_BROKER_URL = os.environ['CELERY_BROKER_URL']

# Eventbrite things.
EVENTBRITE_APP_KEY = os.environ['EVENTBRITE_APP_KEY']
EVENTBRITE_DATE_FMT = '%Y-%m-%dT%H:%M:%SZ'  # utc format only.
