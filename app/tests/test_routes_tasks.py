def test_create_task(client):
    payload = {
        "title": "Test Task",
        "description": "Do something important",
    }
    response = client.post("/tasks", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "New"
    assert "id" in data


def test_get_all_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_task_by_id(client):
    task = client.post(
        "/tasks",
        json={
            "title": "Sample",
            "description": "Details",
        },
    ).json()

    task_id = task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_update_task(client):
    task = client.post(
        "/tasks",
        json={
            "title": "Before Update",
            "description": "Initial",
        },
    ).json()

    task_id = task["id"]
    update = {"title": "After Update"}
    response = client.put(f"/tasks/{task_id}", json=update)
    assert response.status_code == 200
    assert response.json()["title"] == "After Update"


def test_delete_task(client):
    task = client.post(
        "/tasks",
        json={
            "title": "To Be Deleted",
            "description": "Bye",
        },
    ).json()

    task_id = task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.json()["status"] == "New"
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted"


def test_complete_task(client):
    task = client.post(
        "/tasks",
        json={
            "title": "To Be Completed",
            "description": "Do it",
        },
    ).json()

    task_id = task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.json()["status"] == "New"
    response = client.post(f"/tasks/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "Completed"

def test_list_public_tasks(client):
    task1 = client.post("/tasks", json={"title": "Public Task 1", "description": "Desc 1"}).json()
    task2 = client.post("/tasks", json={"title": "Public Task 2", "description": "Desc 2"}).json()

    response = client.get("/tasks/public")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    ids = [task["id"] for task in tasks]
    assert task1["id"] in ids
    assert task2["id"] in ids
