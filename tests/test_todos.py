from http import HTTPStatus

from app.schemas import TodoPublic
from tests.conftest import todos_payload


def test_create_todo(client, auth_headers):
    response = client.post(
        f'/todos/?status={todos_payload[0]["status"]}',
        json={
            'title': todos_payload[0]['title'],
            'description': todos_payload[0]['description'],
        },
        headers=auth_headers,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert isinstance(TodoPublic.model_validate(response.json()), TodoPublic)


def test_get_todos(client, auth_headers):
    response = client.get(
        '/todos/',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert all(
        isinstance(TodoPublic.model_validate(todo), TodoPublic)
        for todo in response.json()
    )


def test_get_todos_with_title(client, auth_headers):
    response = client.get(
        '/todos/?limit=100&offset=0&title=todo',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert all(
        isinstance(TodoPublic.model_validate(todo), TodoPublic)
        for todo in response.json()
    )


def test_get_todos_with_other_filter(client, auth_headers):
    response = client.get(
        '/todos/?limit=100&offset=0&description=descr',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert all(
        isinstance(TodoPublic.model_validate(todo), TodoPublic)
        for todo in response.json()
    )


def test_get_deleted_todos(client, auth_headers):
    response = client.get(
        '/todos/trash',
        headers=auth_headers,
    )
    assert response.status_code == HTTPStatus.OK


def test_empty_trash(client, auth_headers):
    response = client.delete(
        '/todos/trash',
        headers=auth_headers,
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_update_todo_status(client, todo, auth_headers):
    response = client.patch(
        f'/todos/{todo["id"]}/status?status=COMPLETED',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['status'] == 'COMPLETED'


def test_update_todo_data(client, todo, auth_headers):
    response = client.patch(
        f'/todos/{todo["id"]}',
        headers=auth_headers,
        json={
            'title': 'New Title',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'New Title'


def test_delete_todo(client, todo, auth_headers):
    response = client.delete(
        f'/todos/{todo["id"]}',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.NO_CONTENT
