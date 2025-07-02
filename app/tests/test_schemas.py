import pytest
from app.schemas.schemas import (
    UserCreate, UserLogin, Token, TaskCreate,
    TaskUpdate, TaskOut, TaskStatus
)


def test_user_create_valid():
    user = UserCreate(first_name="John", username="johnny", password="secret")
    assert user.first_name == "John"
    assert user.last_name is None

def test_user_create_missing_required():
    with pytest.raises(ValueError):
        UserCreate(username="useronly")

def test_user_login_schema():
    login = UserLogin(username="test", password="pw")
    assert login.username == "test"


def test_token_schema():
    token = Token(access_token="abc123", token_type="bearer")
    assert token.access_token == "abc123"


def test_task_create_schema():
    task = TaskCreate(title="Do thing", description="Details here")
    assert task.title == "Do thing"

def test_task_update_partial():
    update = TaskUpdate(status=TaskStatus.completed)
    assert update.status == TaskStatus.completed

def test_task_update_none_fields():
    update = TaskUpdate()
    assert update.dict(exclude_unset=True) == {}


def test_task_status_enum_str():
    assert TaskStatus.new == "New"
    assert TaskStatus.in_progress == "In Progress"
    assert TaskStatus.completed.value == "Completed"


def test_task_out_from_orm():
    class FakeTask:
        def __init__(self, id, title, description, status):
            self.id = id
            self.title = title
            self.description = description
            self.status = status

    orm_obj = FakeTask(1, "Test", "desc", TaskStatus.in_progress)
    schema = TaskOut.model_validate(orm_obj)
    assert schema.status == TaskStatus.in_progress
    assert schema.title == "Test"

