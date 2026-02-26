from http import HTTPStatus

from app.schemas import UserPublic
from tests.conftest import users_payload


def test_create_user(client):
    response = client.post(
        '/users',
        json=users_payload[0],
    )

    assert response.status_code == HTTPStatus.CREATED
    assert users_payload[0]['username'] == response.json().get('username')
    assert users_payload[0]['email'] == response.json().get('email')
    assert isinstance(response.json().get('id'), str)
    assert len(response.json().get('id')) > 0


def test_create_user_username_conflict(client, user):
    response = client.post(
        '/users',
        json={
            'username': users_payload[0]['username'],
            'email': 'new_email@example.com',
            'password': users_payload[0]['password'],
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already exists.'}


def test_create_user_email_conflict(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'new_username',
            'email': users_payload[0]['email'],
            'password': users_payload[0]['password'],
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already exists.'}


def test_get_users(client, user):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), list)
    assert all(isinstance(db_user, dict) for db_user in response.json())
    assert all(
        isinstance(UserPublic.model_validate(db_user), UserPublic)
        for db_user in response.json()
    )


def test_get_me_user(client, auth_headers):
    response = client.get(
        '/users/me',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), dict)
    assert isinstance(UserPublic.model_validate(response.json()), UserPublic)


def test_get_user_by_id(client, user):
    response = client.get(f'/users/{user["id"]}')

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), dict)
    assert isinstance(UserPublic.model_validate(response.json()), UserPublic)


def test_get_user_by_id_not_found(client):
    response = client.get('/users/false-id-1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User does not exist.'}


def test_update_user(client, user, auth_headers):
    response = client.put(
        f'/users/{user["id"]}',
        json=users_payload[1],
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), dict)
    assert isinstance(UserPublic.model_validate(response.json()), UserPublic)
    assert response.json().get('username') == users_payload[1]['username']


def test_update_user_username_conflict(client, user, other_user, auth_headers):
    response = client.put(
        f'/users/{user["id"]}',
        json={
            'username': other_user['username'],
            'email': 'new_email@example.com',
            'password': 'secret',
        },
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already exists.'}


def test_update_user_email_conflict(client, user, other_user, auth_headers):
    response = client.put(
        f'/users/{user["id"]}',
        json={
            'username': 'db_users[0]name',
            'email': other_user['email'],
            'password': 'secret',
        },
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already exists.'}


def test_update_user_not_found(client, user, mock_get_current_user):
    response = client.put(
        '/users/false-id-1',
        json=users_payload[1],
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User does not exist.'}


def test_partial_update_user_username(client, user, auth_headers):
    response = client.patch(
        f'/users/{user["id"]}',
        json={
            'username': users_payload[0]['username'],
        },
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), dict)
    assert isinstance(UserPublic.model_validate(response.json()), UserPublic)


def test_partial_update_user_email(client, user, auth_headers):
    response = client.patch(
        f'/users/{user["id"]}',
        json={
            'email': 'new_email@example.com',
        },
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), dict)
    assert isinstance(UserPublic.model_validate(response.json()), UserPublic)


def test_partial_update_user_password(client, user, auth_headers):
    response = client.patch(
        f'/users/{user["id"]}',
        json={
            'password': 'new_password',
        },
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json(), dict)
    assert isinstance(UserPublic.model_validate(response.json()), UserPublic)


def test_partial_update_user_username_conflict(client, user, other_user, auth_headers):
    response = client.patch(
        f'/users/{user["id"]}',
        json={
            'username': other_user['username'],
            'email': 'new_email@example.com',
            'password': users_payload[0]['password'],
        },
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already exists.'}


def test_partial_update_user_email_conflict(client, user, other_user, auth_headers):
    response = client.patch(
        f'/users/{user["id"]}',
        json={
            'username': users_payload[0]['username'],
            'email': other_user['email'],
            'password': users_payload[0]['password'],
        },
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'User already exists.'}


def test_partial_update_user_not_found(
    client,
    mock_get_current_user,
):
    response = client.patch(
        '/users/false-id-1',
        json=users_payload[1],
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User does not exist.'}


def test_delete_user(client, user, auth_headers):
    response = client.delete(
        f'/users/{user["id"]}',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'detail': 'User deleted.'}


def test_delete_user_not_found(client, mock_get_current_user):
    response = client.delete(
        '/users/false-id-1',
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User does not exist.'}
