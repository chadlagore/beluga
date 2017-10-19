import os

# Geo config (this is an odd place to put this isnt it).
VANCOUVER_LAT = 49.241
VANCOUVER_LON = -123.1073
VANCOUVER_RAD = "10km"

# Celery eats this stuff automagically.
timezone = 'America/Vancouver'
result_backend = os.environ['CELERY_RESULT_BACKEND']
celery_broker_url = os.environ['CELERY_BROKER_URL']
broker_pool_limit = 0
redis_max_connections = 20  # heroku

# Eventbrite things.
EVENTBRITE_APP_KEY = os.environ['EVENTBRITE_APP_KEY']
EVENTBRITE_DATE_FMT = '%Y-%m-%dT%H:%M:%SZ'  # utc format only.
COLLECTION_INTERVAL = int(os.environ.get('COLLECTION_INTERVAL', 20))
STALE_EVENT_DAYS = int(os.environ.get('STALE_EVENT_DAYS', 5))
