import pytest

from app.schemas.schemas import (PaginatedTasks, TaskCreate, TaskOut,
                                 TaskStatus, TaskUpdate, Token, UserCreate,
                                 UserLogin)


def test_user_create_valid():
    # Creates user with valid info
    user = UserCreate(first_name="Richard", username="Rich", password="secret_pass")
    assert user.first_name == "Richard"
    assert user.last_name is None


def test_user_create_missing_required():
    # Creates user with only username and without a password or first name thereby failing
    with pytest.raises(ValueError):
        UserCreate(username="useronly")


def test_user_login_schema():
    # Logging in with valid info
    login = UserLogin(username="test", password="pw")
    assert login.username == "test"


def test_token_schema():
    # Creating token with valid info
    token = Token(access_token="abc123_special", token_type="bearer")
    assert token.access_token == "abc123_special"


def test_task_create_schema():
    # Creating task with valid info
    task = TaskCreate(title="Do one thing", description="Details")
    assert task.title == "Do one thing"


def test_task_update_partial():
    # Updating task with valid info
    update = TaskUpdate(status=TaskStatus.completed)
    assert update.status == TaskStatus.completed


def test_task_update_none_fields():
    # Updating without new information should do nothing
    update = TaskUpdate()
    assert update.dict(exclude_unset=True) == {}


def test_task_status_enum_str():
    # Checking all valid TaskStatus strings
    assert TaskStatus.new == "New"
    assert TaskStatus.in_progress == "In Progress"
    assert TaskStatus.completed.value == "Completed"


def test_task_out_from_orm():
    # Creating task with orm instead of http request
    class FakeTask:
        def __init__(self, id, title, description, status):
            self.id = id
            self.title = title
            self.description = description
            self.status = status

    orm_obj = FakeTask(1, "Test", "description", TaskStatus.in_progress)
    schema = TaskOut.model_validate(orm_obj)
    assert schema.status == TaskStatus.in_progress
    assert schema.title == "Test"


def test_paginated_tasks_schema():
    # Paginated schema should return proper values for 1 task result
    task = TaskOut(
        id=1,
        title="Test Task Title",
        description="A test task description",
        status=TaskStatus.new,
    )

    paginated = PaginatedTasks(total=1, skip=0, limit=10, tasks=[task])

    assert paginated.total == 1
    assert paginated.skip == 0
    assert paginated.limit == 10
    assert isinstance(paginated.tasks, list)
    assert paginated.tasks[0].title == "Test Task Title"
    assert paginated.tasks[0].status == TaskStatus.new
