from http import HTTPStatus


def test_get_valid_todos(client, auth_headers):
    response = client.patch(
        '/todos/mock-id/status?status=COMPLETED',
        headers=auth_headers,
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}
