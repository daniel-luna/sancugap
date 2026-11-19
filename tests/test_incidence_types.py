def test_create_incidence_type(client, admin_headers):
    response = client.post(
        "/api/v1/incidence-types/",
        json={"slug": "theft", "description": "Theft"},
        headers=admin_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "theft"
    assert data["description"] == "Theft"
    assert "id" in data


def test_create_duplicate_slug(client, admin_headers, incidence_type):
    response = client.post(
        "/api/v1/incidence-types/",
        json={"slug": incidence_type.slug, "description": "Duplicate"},
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_incidence_type_requires_admin(client, user_headers):
    response = client.post(
        "/api/v1/incidence-types/",
        json={"slug": "theft", "description": "Theft"},
        headers=user_headers,
    )
    assert response.status_code == 403


def test_create_incidence_type_no_token(client):
    response = client.post(
        "/api/v1/incidence-types/",
        json={"slug": "theft", "description": "Theft"},
    )
    assert response.status_code == 401


def test_get_all_incidence_types(client, admin_headers, incidence_type):
    response = client.get("/api/v1/incidence-types/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    slugs = [it["slug"] for it in data]
    assert incidence_type.slug in slugs


def test_get_incidence_type_by_id(client, admin_headers, incidence_type):
    response = client.get(
        f"/api/v1/incidence-types/{incidence_type.id}", headers=admin_headers
    )
    assert response.status_code == 200
    assert response.json()["slug"] == incidence_type.slug


def test_get_incidence_type_not_found(client, admin_headers):
    response = client.get("/api/v1/incidence-types/9999", headers=admin_headers)
    assert response.status_code == 404


def test_update_incidence_type(client, admin_headers, incidence_type):
    response = client.put(
        f"/api/v1/incidence-types/{incidence_type.id}",
        json={"description": "Updated description"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["description"] == "Updated description"


def test_update_incidence_type_slug_conflict(client, admin_headers, incidence_type, db_session):
    from core.models import IncidenceType
    other = IncidenceType(slug="other", description="Other")
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)
    response = client.put(
        f"/api/v1/incidence-types/{other.id}",
        json={"slug": incidence_type.slug},
        headers=admin_headers,
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_update_incidence_type_not_found(client, admin_headers):
    response = client.put(
        "/api/v1/incidence-types/9999",
        json={"slug": "nope"},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_delete_incidence_type(client, admin_headers, incidence_type):
    response = client.delete(
        f"/api/v1/incidence-types/{incidence_type.id}", headers=admin_headers
    )
    assert response.status_code == 204


def test_delete_incidence_type_not_found(client, admin_headers):
    response = client.delete("/api/v1/incidence-types/9999", headers=admin_headers)
    assert response.status_code == 404
