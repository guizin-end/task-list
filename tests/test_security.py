from datetime import datetime, timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from freezegun import freeze_time


def test_authenticate_user_not_found(client):
    response = client.post(
        '/auth/token',
        data={
            'username': 'invalid_username',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username or password.'}


def test_authenticate_user_invalid_password(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user['username'],
            'password': 'invalid_password',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username or password.'}


def test_get_current_user_no_username_in_payload(
    client, user, mock_decode_payload_no_username, auth_headers
):
    response = client.delete(
        f'/users/{user["id"]}/',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_not_found(
    client, user, auth_headers, mock_decode_payload_with_mock_username
):
    response = client.delete(
        f'/users/{user["id"]}/',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


@freeze_time(datetime.now(tz=ZoneInfo('UTC')) + timedelta(minutes=60))
def test_get_current_user_expired_token(client, user, auth_headers):
    response = client.delete(
        f'/users/{user["id"]}/',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
