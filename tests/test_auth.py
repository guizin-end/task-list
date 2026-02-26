from http import HTTPStatus


def test_login_unauthorized(client, mock_authenticate_user):
    response = client.post(
        '/auth/token',
        data={
            'username': 'invalid_username',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password.'}
