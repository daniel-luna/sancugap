def test_register_success(client, admin_headers, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "new123",
            "role": "user",
        },
        headers=admin_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@test.com"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data


def test_register_duplicate_username(client, admin_headers, regular_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": regular_user.username,
            "email": "other@test.com",
            "password": "new123",
            "role": "user",
        },
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_duplicate_email(client, admin_headers, regular_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "anotheruser",
            "email": regular_user.email,
            "password": "new123",
            "role": "user",
        },
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_requires_admin(client, user_headers):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "new123",
            "role": "user",
        },
        headers=user_headers,
    )
    assert response.status_code == 403


def test_register_no_token(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "new123",
            "role": "user",
        },
    )
    assert response.status_code == 401


def test_login_success(client, regular_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": regular_user.username, "password": "user123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, regular_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": regular_user.username, "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_login_inactive_user(client, inactive_user):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": inactive_user.username, "password": "inactive123"},
    )
    assert response.status_code == 400
    assert "Inactive user" in response.json()["detail"]


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody", "password": "nopass"},
    )
    assert response.status_code == 401


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "API de Gestión de Usuarios" in data["message"]


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
