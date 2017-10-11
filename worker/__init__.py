from celery import Celery

import worker.config as config

# Create a celery worker.
celery = Celery(
    __name__,
    backend=config.CELERY_RESULT_BACKEND,
    broker=config.CELERY_BROKER_URL
)

celery.config_from_object(config)
