import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth.auth import get_password_hash
from app.db.deps import get_db
from app.db.session import Base
from app.main import app
from app.models.models import User

load_dotenv(dotenv_path=".env.test")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if TEST_DATABASE_URL is None:
    raise RuntimeError("TEST_DATABASE_URL must be set")

engine = create_engine(TEST_DATABASE_URL)


TestingSessionLocal = sessionmaker(  # Replaces SessionLocal
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="session", autouse=True)
def initialize_database():  # Creates schema before every test and wipes it after each test session
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def clean_tables(db_session):  # Fallback after drop_all in initialize_database. Wipe data from database after each test
    yield
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


@pytest.fixture(scope="function")
def db_session():  # Creates a session for every HTTP request for tests
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):  # Provides a test client for making HTTP requests
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db  # Uses TEST_DATABASE_URL instead of DATABASE_URL

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def create_users(db_session):  # Creates 2 users to use in tests
    pw = "testpass123"
    u1 = User(first_name="Test", last_name="User1", username="user1", password=get_password_hash(pw))
    u2 = User(first_name="Test", last_name="User2", username="user2", password=get_password_hash(pw))
    db_session.add_all([u1, u2])
    db_session.commit()
    db_session.refresh(u1)
    db_session.refresh(u2)
    return {"user1": {"username": "user1", "password": pw},
            "user2": {"username": "user2", "password": pw}}

@pytest.fixture(scope="function")
def token_headers(client, create_users):  # Used for authenticating user1 with an authentication token
    creds = create_users["user1"]
    resp = client.post("/auth/login", json={"username": creds['username'], "password": creds['password']})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def other_token_headers(client, create_users):  # Enables access testing beyond if the user is just signed in
    creds = create_users["user2"]
    resp = client.post("/auth/login", json={"username": creds['username'], "password": creds['password']})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
