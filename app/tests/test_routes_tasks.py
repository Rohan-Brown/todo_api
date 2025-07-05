import pytest
from fastapi.testclient import TestClient

from app.models.models import Task, TaskStatus, User

"""
Some functions use token_headers and other_token_headers. The purpose is to distinguish between users. E.g. Can task
with created with token_header be updated or deleted with other_token_headers?
"""
"""
"/tasks/filter-by-status/" only exist because it was specified in task requirements. Read more about it in README file.
"""

def test_requires_authentication(client: TestClient):
    # Tests all endpoints in routes_task for user authentication
    endpoints = [
        ("get", "/tasks"),
        ("post", "/tasks"),
        ("get", "/tasks/1"),
        ("put", "/tasks/1"),
        ("delete", "/tasks/1"),
        ("put", "/tasks/1/complete"),
        ("get", "/tasks/public"),
    ]
    for method, url in endpoints:
        resp = getattr(client, method)(url)
        assert resp.status_code == 403  # Custom code for no access instead of 401


def test_create_and_read_tasks(token_headers: dict, client: TestClient):
    # GET and POST methods for task with valid input
    payload = {"title": "Test Important Task", "description": "Do something important"}
    resp = client.post("/tasks", json=payload, headers=token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == payload["title"]
    assert data["status"] == TaskStatus.new.value
    assert "id" in data

    task_id = data["id"]
    resp2 = client.get(f"/tasks/{task_id}", headers=token_headers)
    assert resp2.status_code == 200
    assert resp2.json()["id"] == task_id


def test_update_and_delete_task(token_headers: dict, client: TestClient):
    # PUT and DELETE methods for task with valid inputs
    resp = client.post(
        "/tasks", json={"title": "Created", "description": "my_desciption"}, headers=token_headers
    )
    task_id = resp.json()["id"]

    resp2 = client.put(
        f"/tasks/{task_id}", json={"title": "Updated"}, headers=token_headers
    )
    assert resp2.status_code == 200
    assert resp2.json()["title"] == "Updated"

    resp3 = client.delete(f"/tasks/{task_id}", headers=token_headers)
    assert resp3.status_code == 200
    assert resp3.json()["message"] == "Task deleted"

def test_list_user_tasks(token_headers: dict, client: TestClient):
    # Should return user tasks
    client.post("/tasks", json={"title": "A"}, headers=token_headers)
    client.post("/tasks", json={"title": "B"}, headers=token_headers)
    resp = client.get("/tasks", headers=token_headers)
    data = resp.json()
    assert isinstance(data.get("tasks"), list)
    assert len(data["tasks"]) == 2



def test_cannot_get_other_users_task(token_headers: dict, other_token_headers: dict, client: TestClient):
    # Checks if other users can access task details of another user with GET method
    resp = client.post("/tasks", json={"title": "User1 Task"}, headers=token_headers)
    tid = resp.json()["id"]
    resp2 = client.get(f"/tasks/{tid}", headers=other_token_headers)
    assert resp2.status_code == 403

def test_cannot_update_other_users_task(token_headers: dict, other_token_headers: dict, client: TestClient):
    # Checks if other users can update task details of another user with PUT method
    resp = client.post("/tasks", json={"title": "User1 Task"}, headers=token_headers)
    tid = resp.json()["id"]
    resp2 = client.put(f"/tasks/{tid}", json={"title": "You have been hacked"}, headers=other_token_headers)
    assert resp2.status_code == 403

def test_cannot_delete_other_users_task(token_headers: dict, other_token_headers: dict, client: TestClient):
    # Checks if other users can delete task of another user with DELETE method

    resp = client.post("/tasks", json={"title": "User1 Task"}, headers=token_headers)
    tid = resp.json()["id"]
    resp2 = client.delete(f"/tasks/{tid}", headers=other_token_headers)
    assert resp2.status_code == 403

def test_cannot_complete_other_users_task(token_headers, other_token_headers, client):
    # Checks if other users can set task status to complete even if the task doesn't belong to them with PUT method

    t = client.post("/tasks", json={"title": "User1"}, headers=token_headers).json()
    resp = client.put(f"/tasks/{t['id']}/complete", headers=other_token_headers)
    assert resp.status_code == 403

def test_not_found_vs_forbidden(token_headers: dict, other_token_headers: dict, client: TestClient):
    # Distinguish from a not found error(404) and a no access error(403)
    resp1 = client.get("/tasks/9999", headers=token_headers)
    assert resp1.status_code == 404

    resp2 = client.post("/tasks", json={"title": "private"}, headers=token_headers)
    tid = resp2.json()["id"]
    resp3 = client.delete(f"/tasks/{tid}", headers=other_token_headers)
    assert resp3.status_code == 403

def test_public_list_multiple_users(token_headers: dict, other_token_headers: dict, client: TestClient):
    # Tests if user can see anyone's tasks in /tasks/public
    client.post("/tasks", json={"title": "Public1"}, headers=token_headers)
    client.post("/tasks", json={"title": "Public2"}, headers=other_token_headers)
    resp = client.get("/tasks/public", headers=token_headers)
    assert resp.status_code == 200
    assert len(resp.json()["tasks"]) >= 2

def test_get_nonexistent_task_returns_404(token_headers: dict, client: TestClient):
    # Checks if status error is 404 when using GET method on a task that doesn't exist
    resp = client.get("/tasks/9999", headers=token_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Task not found"

def test_update_nonexistent_task_returns_404(token_headers: dict, client: TestClient):
    # Checks if status error is 404 when updating info using PUT method on a task that doesn't exist
    resp = client.put("/tasks/9999", json={"title": "DifferentTitle"}, headers=token_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Task not found"


def test_delete_nonexistent_task_returns_404(token_headers: dict, client: TestClient):
    # Checks if status code error is 404 when deleting a task using DELETE method on a task that doesn't exist
    resp = client.delete("/tasks/9999", headers=token_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Task not found"

def test_complete_nonexistent_task_returns_404(token_headers: dict, client: TestClient):
    # Checks if status code error is 404 when updating status to complete using PUT method on a task that doesn't exist
    resp = client.put("/tasks/9999/complete", headers=token_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Task not found"

def test_create_task_missing_title(token_headers: dict, client: TestClient):
    # Creating a task without a title should fail
    resp = client.post(
        "/tasks", json={"description": "no title"}, headers=token_headers
    )
    assert resp.status_code == 422

def test_update_missing_title(token_headers: dict, client: TestClient):
    # Updating without a title should fail
    resp = client.post("/tasks", json={"title": "Valid"}, headers=token_headers)
    tid = resp.json()["id"]
    resp2 = client.put(f"/tasks/{tid}", json={"title": ""}, headers=token_headers)
    assert resp2.status_code == 422

def test_invalid_status_filter_returns_422(token_headers, client):
    # Filtering by invalid status string returns 422 error
    resp = client.get("/tasks?status=InvalidStatus", headers=token_headers)
    assert resp.status_code == 422

def test_negative_skip_limit_return_422(token_headers, client):
    # Paginating with negative values returns error status code
    resp = client.get("/tasks?skip=-1&limit=-5", headers=token_headers)
    assert resp.status_code == 422

def test_mark_complete_twice(token_headers: dict, client: TestClient):
    # Updating task status to complete twice returns complete without any errors
    resp = client.post("/tasks", json={"title": "complete_twice"}, headers=token_headers)
    tid = resp.json()["id"]
    client.put(f"/tasks/{tid}/complete", headers=token_headers)
    resp2 = client.put(f"/tasks/{tid}/complete", headers=token_headers)
    assert resp2.status_code == 200
    assert resp2.json()["status"] == TaskStatus.completed.value




def test_filter_by_status_endpoint(token_headers: dict, client: TestClient):
    # Testing filter_by_status with valid inputs
    t1 = client.post("/tasks", json={"title": "Todo"}, headers=token_headers).json()
    client.post(f"/tasks/{t1['id']}/complete", headers=token_headers)
    resp = client.get("/tasks/filter-by-status/?status=Completed", headers=token_headers)
    assert resp.status_code == 200
    assert all(t["status"] == TaskStatus.completed.value for t in resp.json()["tasks"])


def test_public_pagination(token_headers: dict, client: TestClient):
    # Should return pagination logic for number of tasks regardless of owner
    for i in range(5):
        client.post("/tasks", json={"title": f"P{i}"}, headers=token_headers)
    resp = client.get("/tasks/public?skip=2&limit=2", headers=token_headers)
    data = resp.json()
    assert data["total"] >= 5
    assert data["skip"] == 2
    assert data["limit"] == 2
    assert len(data["tasks"]) == 2

def test_user_pagination(token_headers: dict, client: TestClient):
    # Should return pagination logic for a number of user tasks

    for i in range(5):
        client.post("/tasks", json={"title": f"U{i}"}, headers=token_headers)
    resp = client.get("/tasks?skip=2&limit=2", headers=token_headers)
    data = resp.json()
    assert data["total"] >= 5
    assert data["skip"] == 2
    assert data["limit"] == 2
    assert len(data["tasks"]) == 2


def test_filter_and_pagination(token_headers: dict, client: TestClient):
    # Creates 5 tasks 2 of which are given the status 'Complete'. Filtering for 'Complete' 2 tasks should be returned
    # Pagination should return one page with 1 task each
    for i in range(3):
        client.post("/tasks", json={"title": f"New{i}"}, headers=token_headers)
    completed_ids = []
    for j in range(2):
        t = client.post("/tasks", json={"title": f"Comp{j}"}, headers=token_headers).json()
        completed_ids.append(t["id"])
        client.put(f"/tasks/{t['id']}/complete", headers=token_headers)

    resp = client.get(
        "/tasks?status=Completed&skip=1&limit=1", headers=token_headers
    )
    data = resp.json()
    assert all(t["status"] == TaskStatus.completed.value for t in data["tasks"])
    assert data["total"] == 2
    assert data["skip"] == 1
    assert data["limit"] == 1
    assert len(data["tasks"]) == 1

def test_public_filter_by_status(token_headers: dict, client: TestClient):
    # Filtering by status 'Complete' on public task page should return tasks with status 'Complete'
    t = client.post("/tasks", json={"title": "Should be completed"}, headers=token_headers).json()
    client.put(f"/tasks/{t['id']}/complete", headers=token_headers)

    resp = client.get("/tasks/public?status=Completed", headers=token_headers)
    assert resp.status_code == 200
    assert all(task["status"] == TaskStatus.completed.value for task in resp.json()["tasks"])


def test_cascade_delete_user(db_session):
    # Deleting user has no endpoint using database delete. When user is deleted that user's tasks should be deleted
    u = User(first_name="DeleteFName", last_name="DeleteLName", username="DeleteUsername", password="Deletepass")
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    t = Task(title="DeleteTitle", user_id=u.id)
    db_session.add(t)
    db_session.commit()
    db_session.refresh(t)
    existing_task = db_session.query(Task).filter_by(id=t.id).first()
    assert existing_task.title == "DeleteTitle", "Task title mismatch"
    db_session.delete(u)
    db_session.commit()
    deleted_task = db_session.query(Task).filter_by(id=t.id).first()
    assert deleted_task is None, "Task should be deleted after user deletion due to cascade"

def test_filter_by_status_pagination(token_headers, client):
    # Same as test_public_filter_by_status except not public only returns user tasks
    for i in range(10):
        client.post("/tasks", json={"title": f"New{i}"}, headers=token_headers)
    completed_tasks = []
    for j in range(5):
        t = client.post("/tasks", json={"title": f"Comp{j}"}, headers=token_headers).json()
        client.put(f"/tasks/{t['id']}/complete", headers=token_headers)
        completed_tasks.append(t)

    resp = client.get("/tasks/filter-by-status/?status=Completed&skip=0&limit=3", headers=token_headers)
    data = resp.json()
    assert resp.status_code == 200
    assert data["total"] == 5
    assert data["skip"] == 0
    assert data["limit"] == 3
    assert len(data["tasks"]) == 3
    assert all(t["status"] == TaskStatus.completed.value for t in data["tasks"])

def test_filter_by_status_invalid_status(token_headers, client):
    # Checks if filtering by invalid status is possible
    resp = client.get("/tasks/filter-by-status/?status=InvalidStatus", headers=token_headers)
    assert resp.status_code == 422
