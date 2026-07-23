import pytest
import os
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def isolated_data_file(tmp_path, monkeypatch):
    """Each test gets its own temporary students.json so tests don't interfere."""
    import app.main as main_module
    data_file = str(tmp_path / "students.json")
    monkeypatch.setattr(main_module, "DATA_FILE", data_file)
    yield


from app.main import app

client = TestClient(app)


# --- Test 1: Root endpoint ---
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


# --- Test 2: Health check ---
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# --- Test 3: Get students – empty list ---
def test_get_students_empty():
    response = client.get("/students")
    assert response.status_code == 200
    assert response.json() == []


# --- Test 4: Create a student ---
def test_create_student():
    payload = {"name": "Alice", "email": "alice@example.com", "grade": "A"}
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["grade"] == "A"
    assert "id" in data


# --- Test 5: Get students – returns created student ---
def test_get_students_after_create():
    client.post("/students", json={"name": "Bob", "email": "bob@example.com", "grade": "B"})
    response = client.get("/students")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Bob"


# --- Test 6: Get student by ID ---
def test_get_student_by_id():
    create_resp = client.post("/students", json={"name": "Carol", "email": "carol@example.com", "grade": "A"})
    student_id = create_resp.json()["id"]
    response = client.get(f"/students/{student_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Carol"


# --- Test 7: Get student by ID – not found ---
def test_get_student_not_found():
    response = client.get("/students/999")
    assert response.status_code == 404


# --- Test 8: Update a student ---
def test_update_student():
    create_resp = client.post("/students", json={"name": "Dave", "email": "dave@example.com", "grade": "C"})
    student_id = create_resp.json()["id"]
    update_payload = {"name": "Dave Updated", "email": "dave@example.com", "grade": "A"}
    response = client.put(f"/students/{student_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Dave Updated"
    assert response.json()["grade"] == "A"


# --- Test 9: Delete a student ---
def test_delete_student():
    create_resp = client.post("/students", json={"name": "Eve", "email": "eve@example.com", "grade": "B"})
    student_id = create_resp.json()["id"]
    delete_resp = client.delete(f"/students/{student_id}")
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Student deleted"
    # Verify student no longer exists
    get_resp = client.get(f"/students/{student_id}")
    assert get_resp.status_code == 404
