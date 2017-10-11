import os


# Environment we need to collect.
DATABASE_URL = os.environ.get('DATABASE_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
EVENTBRITE_APP_KEY = os.environ.get('EVENTBRITE_APP_KEY')


# Geo config.
VANCOUVER_LAT = "49.241"
VANCOUVER_LON = "-123.1073"
VANCOUVER_RAD = "10km"
