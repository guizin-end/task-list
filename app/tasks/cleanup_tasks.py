from datetime import UTC, datetime, timedelta

from sqlalchemy import delete

from app.database import sync_session_factory
from app.models import Todo, TodoStatus
from app.settings import get_settings
from app.tasks.celery_app import celery_app

settings = get_settings()


@celery_app.task(ignore_result=True)
def trash_cleaner():
    time_diff = datetime.now(UTC).replace(tzinfo=None) - timedelta(
        days=settings.TODO_TRASH_EXPIRE_DAYS
    )

    with sync_session_factory() as session:
        session.execute(
            delete(Todo).where(
                Todo.status == TodoStatus.TRASH, Todo.updated_at <= time_diff
            )
        )
        session.commit()
