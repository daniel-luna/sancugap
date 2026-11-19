def test_create_sub_type(client, admin_headers, incidence_type):
    response = client.post(
        "/api/v1/incidence-sub-types/",
        json={
            "type_id": incidence_type.id,
            "slug": "pickpocket",
            "description": "Pickpocket",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "pickpocket"
    assert data["type_id"] == incidence_type.id
    assert "id" in data


def test_create_sub_type_missing_parent(client, admin_headers):
    response = client.post(
        "/api/v1/incidence-sub-types/",
        json={
            "type_id": 9999,
            "slug": "pickpocket",
            "description": "Pickpocket",
        },
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "Incidence type not found" in response.json()["detail"]


def test_create_sub_type_requires_admin(client, user_headers, incidence_type):
    response = client.post(
        "/api/v1/incidence-sub-types/",
        json={
            "type_id": incidence_type.id,
            "slug": "pickpocket",
            "description": "Pickpocket",
        },
        headers=user_headers,
    )
    assert response.status_code == 403


def test_create_sub_type_no_token(client, incidence_type):
    response = client.post(
        "/api/v1/incidence-sub-types/",
        json={
            "type_id": incidence_type.id,
            "slug": "pickpocket",
            "description": "Pickpocket",
        },
    )
    assert response.status_code == 401


def test_get_all_sub_types(client, admin_headers, incidence_sub_type):
    response = client.get("/api/v1/incidence-sub-types/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    slugs = [st["slug"] for st in data]
    assert incidence_sub_type.slug in slugs


def test_get_sub_type_by_id(client, admin_headers, incidence_sub_type):
    response = client.get(
        f"/api/v1/incidence-sub-types/{incidence_sub_type.id}",
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["slug"] == incidence_sub_type.slug


def test_get_sub_type_not_found(client, admin_headers):
    response = client.get("/api/v1/incidence-sub-types/9999", headers=admin_headers)
    assert response.status_code == 404


def test_update_sub_type(client, admin_headers, incidence_sub_type):
    response = client.put(
        f"/api/v1/incidence-sub-types/{incidence_sub_type.id}",
        json={"description": "Updated sub type"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated sub type"


def test_update_sub_type_nonexistent_parent(client, admin_headers, incidence_sub_type):
    response = client.put(
        f"/api/v1/incidence-sub-types/{incidence_sub_type.id}",
        json={"type_id": 9999},
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "Incidence type not found" in response.json()["detail"]


def test_update_sub_type_not_found(client, admin_headers):
    response = client.put(
        "/api/v1/incidence-sub-types/9999",
        json={"slug": "nope"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_delete_sub_type(client, admin_headers, incidence_sub_type):
    response = client.delete(
        f"/api/v1/incidence-sub-types/{incidence_sub_type.id}",
        headers=admin_headers,
    )
    assert response.status_code == 204


def test_delete_sub_type_not_found(client, admin_headers):
    response = client.delete("/api/v1/incidence-sub-types/9999", headers=admin_headers)
    assert response.status_code == 404
