from celery import Celery
from celery.schedules import crontab

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
    beat_schedule={
        'cleanup_tasks': {
            'task': 'app.tasks.cleanup_tasks.trash_cleaner',
            'schedule': crontab(
                hour=0,
                minute=0,
                day_of_month=f'*/{settings.TODO_TRASH_CLEANUP_INTERVAL_DAYS}',
            ),
        }
    },
)

celery_app.autodiscover_tasks(
    ['app.tasks'],
    related_name='cleanup_tasks',
    force=True,
)
