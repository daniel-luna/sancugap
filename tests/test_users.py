def test_get_all_users_admin(client, admin_headers, regular_user, another_user):
    response = client.get("/api/v1/users", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    usernames = [u["username"] for u in data]
    assert regular_user.username in usernames
    assert another_user.username in usernames


def test_get_all_users_non_admin_forbidden(client, user_headers):
    response = client.get("/api/v1/users", headers=user_headers)
    assert response.status_code == 403


def test_get_all_users_no_token(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 401


def test_get_user_by_id_admin(client, admin_headers, regular_user):
    response = client.get(f"/api/v1/users/{regular_user.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["username"] == regular_user.username


def test_get_user_self(client, user_headers, regular_user):
    response = client.get(f"/api/v1/users/{regular_user.id}", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["username"] == regular_user.username


def test_get_user_other_forbidden(client, user_headers, another_user):
    response = client.get(f"/api/v1/users/{another_user.id}", headers=user_headers)
    assert response.status_code == 403


def test_get_user_not_found(client, admin_headers):
    response = client.get("/api/v1/users/9999", headers=admin_headers)
    assert response.status_code == 404


def test_update_self_username(client, user_headers, regular_user):
    response = client.put(
        f"/api/v1/users/{regular_user.id}",
        json={"username": "updateduser"},
        headers=user_headers,
    )
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"


def test_update_self_email(client, user_headers, regular_user):
    response = client.put(
        f"/api/v1/users/{regular_user.id}",
        json={"email": "updated@test.com"},
        headers=user_headers,
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@test.com"


def test_update_self_password(client, user_headers, regular_user, db_session):
    response = client.put(
        f"/api/v1/users/{regular_user.id}",
        json={"password": "newpass123"},
        headers=user_headers,
    )
    assert response.status_code == 200
    from core.auth import verify_password
    db_session.refresh(regular_user)
    assert verify_password("newpass123", regular_user.hashed_password)


def test_update_username_conflict(client, user_headers, regular_user, another_user):
    response = client.put(
        f"/api/v1/users/{regular_user.id}",
        json={"username": another_user.username},
        headers=user_headers,
    )
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


def test_update_email_conflict(client, user_headers, regular_user, another_user):
    response = client.put(
        f"/api/v1/users/{regular_user.id}",
        json={"email": another_user.email},
        headers=user_headers,
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_update_user_not_found(client, admin_headers):
    response = client.put(
        "/api/v1/users/9999",
        json={"username": "nobody"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_update_role_by_admin(client, admin_headers, regular_user):
    response = client.put(
        f"/api/v1/users/{regular_user.id}",
        json={"role": "admin"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_update_role_by_user_ignored(client, user_headers, regular_user, db_session):
    response = client.put(
        f"/api/v1/users/{regular_user.id}",
        json={"role": "admin"},
        headers=user_headers,
    )
    assert response.status_code == 200
    db_session.refresh(regular_user)
    assert regular_user.role.value == "user"


def test_update_is_active_by_admin(client, admin_headers, regular_user):
    response = client.put(
        f"/api/v1/users/{regular_user.id}",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_delete_user_admin(client, admin_headers, regular_user):
    response = client.delete(
        f"/api/v1/users/{regular_user.id}", headers=admin_headers
    )
    assert response.status_code == 204


def test_delete_user_not_found(client, admin_headers):
    response = client.delete("/api/v1/users/9999", headers=admin_headers)
    assert response.status_code == 404


def test_delete_user_non_admin_forbidden(client, user_headers, another_user):
    response = client.delete(f"/api/v1/users/{another_user.id}", headers=user_headers)
    assert response.status_code == 403


def test_get_me(client, user_headers, regular_user):
    response = client.get("/api/v1/me", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["username"] == regular_user.username


def test_get_me_no_token(client):
    response = client.get("/api/v1/me")
    assert response.status_code == 401
