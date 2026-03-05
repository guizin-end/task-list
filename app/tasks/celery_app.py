from celery import Celery

from app.settings import Settings

settings = Settings()


celery_app = Celery(
    'worker',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
