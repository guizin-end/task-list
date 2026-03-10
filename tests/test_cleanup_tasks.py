from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import freezegun

from app.settings import Settings
from app.tasks.cleanup_tasks import trash_cleaner

settings = Settings()


TRASH_URL = '/todos/trash'


def test_todo_trash_cleaner_removes_expired_todo(
    client, mock_sync_session_for_tasks, delete_todo, auth_headers
):
    response = client.get(TRASH_URL, headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1

    cleanup_time = datetime.now(UTC).replace(tzinfo=None) + timedelta(
        days=settings.TODO_TRASH_EXPIRE_DAYS
    )
    with freezegun.freeze_time(cleanup_time):
        trash_cleaner()

    response = client.get(TRASH_URL, headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_todo_trash_cleaner_does_not_remove_before_expiry(
    client, mock_sync_session_for_tasks, delete_todo, auth_headers
):
    response = client.get(TRASH_URL, headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1

    cleanup_time = datetime.now(UTC).replace(tzinfo=None) + timedelta(
        days=settings.TODO_TRASH_EXPIRE_DAYS - 1
    )
    with freezegun.freeze_time(cleanup_time):
        trash_cleaner()

    response = client.get(TRASH_URL, headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
