def test_create_incidence(client, user_headers, incidence_type):
    response = client.post(
        "/api/v1/incidences/",
        json={
            "type_id": incidence_type.id,
            "latitude": -33.456,
            "longitude": -70.648,
            "active": True,
        },
        headers=user_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type_id"] == incidence_type.id
    assert abs(data["latitude"] - (-33.456)) < 0.001
    assert abs(data["longitude"] - (-70.648)) < 0.001
    assert data["active"] is True
    assert data["user_id"] is not None
    assert "id" in data


def test_create_incidence_with_sub_type(client, user_headers, incidence_type, incidence_sub_type):
    response = client.post(
        "/api/v1/incidences/",
        json={
            "type_id": incidence_type.id,
            "sub_type_id": incidence_sub_type.id,
            "latitude": -33.456,
            "longitude": -70.648,
        },
        headers=user_headers,
    )
    assert response.status_code == 201
    assert response.json()["sub_type_id"] == incidence_sub_type.id


def test_create_incidence_invalid_type(client, user_headers):
    response = client.post(
        "/api/v1/incidences/",
        json={
            "type_id": 9999,
            "latitude": -33.456,
            "longitude": -70.648,
        },
        headers=user_headers,
    )
    assert response.status_code == 400
    assert "Incidence type not found" in response.json()["detail"]


def test_create_incidence_invalid_sub_type(client, user_headers, incidence_type):
    response = client.post(
        "/api/v1/incidences/",
        json={
            "type_id": incidence_type.id,
            "sub_type_id": 9999,
            "latitude": -33.456,
            "longitude": -70.648,
        },
        headers=user_headers,
    )
    assert response.status_code == 400
    assert "Incidence sub type not found" in response.json()["detail"]


def test_create_incidence_no_token(client, incidence_type):
    response = client.post(
        "/api/v1/incidences/",
        json={
            "type_id": incidence_type.id,
            "latitude": -33.456,
            "longitude": -70.648,
        },
    )
    assert response.status_code == 401


def test_get_all_incidences_admin(client, admin_headers, user_headers, incidence_type, regular_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=regular_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    response = client.get("/api/v1/incidences/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_all_incidences_user_sees_own(client, user_headers, incidence_type, regular_user, another_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc1 = Incidence(
        user_id=regular_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    inc2 = Incidence(
        user_id=another_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.457, -70.649),
        active=True,
    )
    db_session.add_all([inc1, inc2])
    db_session.commit()
    response = client.get("/api/v1/incidences/", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == regular_user.id


def test_get_incidence_by_id_owner(client, user_headers, incidence_type, regular_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=regular_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    db_session.refresh(inc)
    response = client.get(f"/api/v1/incidences/{inc.id}", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["id"] == inc.id


def test_get_incidence_by_id_admin(client, admin_headers, incidence_type, regular_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=regular_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    db_session.refresh(inc)
    response = client.get(f"/api/v1/incidences/{inc.id}", headers=admin_headers)
    assert response.status_code == 200


def test_get_incidence_by_id_forbidden(client, user_headers, incidence_type, another_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=another_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    db_session.refresh(inc)
    response = client.get(f"/api/v1/incidences/{inc.id}", headers=user_headers)
    assert response.status_code == 403


def test_get_incidence_not_found(client, admin_headers):
    response = client.get("/api/v1/incidences/9999", headers=admin_headers)
    assert response.status_code == 404


def test_update_incidence_owner(client, user_headers, incidence_type, regular_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=regular_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    db_session.refresh(inc)
    response = client.put(
        f"/api/v1/incidences/{inc.id}",
        json={"active": False},
        headers=user_headers,
    )
    assert response.status_code == 200
    assert response.json()["active"] is False


def test_update_incidence_admin(client, admin_headers, incidence_type, regular_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=regular_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    db_session.refresh(inc)
    response = client.put(
        f"/api/v1/incidences/{inc.id}",
        json={"latitude": -33.5, "longitude": -70.6},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert abs(response.json()["latitude"] - (-33.5)) < 0.001


def test_update_incidence_forbidden(client, user_headers, incidence_type, another_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=another_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    db_session.refresh(inc)
    response = client.put(
        f"/api/v1/incidences/{inc.id}",
        json={"active": False},
        headers=user_headers,
    )
    assert response.status_code == 403


def test_update_incidence_not_found(client, admin_headers):
    response = client.put(
        "/api/v1/incidences/9999",
        json={"active": False},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_delete_incidence_owner(client, user_headers, incidence_type, regular_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=regular_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    db_session.refresh(inc)
    response = client.delete(f"/api/v1/incidences/{inc.id}", headers=user_headers)
    assert response.status_code == 204


def test_delete_incidence_admin(client, admin_headers, incidence_type, regular_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=regular_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    db_session.refresh(inc)
    response = client.delete(f"/api/v1/incidences/{inc.id}", headers=admin_headers)
    assert response.status_code == 204


def test_delete_incidence_forbidden(client, user_headers, incidence_type, another_user, db_session):
    from core.models import Incidence
    from api.v1.endpoints.incidences import lat_lon_to_point
    inc = Incidence(
        user_id=another_user.id,
        type_id=incidence_type.id,
        coordinate=lat_lon_to_point(-33.456, -70.648),
        active=True,
    )
    db_session.add(inc)
    db_session.commit()
    db_session.refresh(inc)
    response = client.delete(f"/api/v1/incidences/{inc.id}", headers=user_headers)
    assert response.status_code == 403


def test_delete_incidence_not_found(client, admin_headers):
    response = client.delete("/api/v1/incidences/9999", headers=admin_headers)
    assert response.status_code == 404
