import os


# Environment we need to collect.
DATABASE_URL = os.environ.get('DATABASE_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')