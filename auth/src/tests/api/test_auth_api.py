def test_me_success(client, override_current_user):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json() == {
        "user_id": "123",
        "roles": ["user"],
    }


def test_me_unauthorized(client, override_invalid_user):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_admin_success(client, override_admin):
    response = client.get("/api/v1/auth/admin")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome admin"}


def test_admin_forbidden(client, override_current_user):
    response = client.get("/api/v1/auth/admin")
    assert response.status_code == 403
