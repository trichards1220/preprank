from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_schools_returns_200():
    response = client.get("/api/v1/schools/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_schools_filter_by_division():
    response = client.get("/api/v1/schools/?division=I")
    assert response.status_code == 200
    data = response.json()
    for school in data:
        assert school["division"] == "I"


def test_list_schools_filter_by_classification():
    response = client.get("/api/v1/schools/?classification=5A")
    assert response.status_code == 200
    data = response.json()
    for school in data:
        assert school["classification"] == "5A"


def test_get_school_by_id():
    list_resp = client.get("/api/v1/schools/?limit=1")
    schools = list_resp.json()
    if len(schools) == 0:
        return
    school_id = schools[0]["id"]
    response = client.get(f"/api/v1/schools/{school_id}")
    assert response.status_code == 200
    assert response.json()["id"] == school_id


def test_get_school_not_found():
    response = client.get("/api/v1/schools/999999")
    assert response.status_code == 404
