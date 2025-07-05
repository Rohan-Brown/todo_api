# ToDoList API Application
## ###Please contact me in Telegram if you are confused about any design choices, or if you think something is missing###
This is a functioning API-based ToDoList application built with PostgreSQL, FastAPI, and Docker. It implements JWT registration and authentication, CRUD and minimal templating: static HTML files (for example login.html) are served directly without Jinja2.

---

## 1. **Features**
The following features are implemented in the application:
- Simple frontend for basic operations
- User authentication and registration with JWT
- Token-based authentication
- CRUD features for tasks
- Complete testing setup with pytest
- Pagination for the 'get_all_tasks' endpoint and for the 'get_all_user_tasks' endpoint (public and private, respectively)
- Status filtering: 'New', 'In Progress', 'Completed'
- Task privatization (only the task owner can update or delete their own tasks)
- Rollback-safe database error-handling
- Pre-commit security with Gitleaks and Bandit
- Safe commits with pre-commit pytest coverage minimum 90%
- Containerized deployment with Docker

---

## 2. **Technologies**

- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker
- Uvicorn
- Pydantic
- Pytest
- Coverage
- Pre-commit
- JWT Authentication

---

## 3. **Requirements**

- Python 3.12+
- Docker 27.5+
- PostgreSQL 12+ (if running outside Docker)

---

## 4. **Example `.env` File**

```env
DATABASE_URL=postgresql://username:password@host:5432/database_name
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydb
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

---
## 5. **Installation**
Open Windows PowerShell and run this
```bash
git clone https://github.com/Rohan-Brown/todo_api.git
cd todo_api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pre-commit install
Copy-Item .env.example .env
```
---

## 6. **Developer Notes**


- Assuming 6 symbols required for the password field means 6 characters and not 6 special characters e.g. (@, #, $)

- Decided to use TaskStatus model instead of using 'constr' with 'regex' or 'Literal'. Using TaskStatus model for ease of use and because it follows best practices.

- Added filter_task_by_status and mark_complete endpoints only to satisfy task requirements. They don't appear in the frontend and aren't reused in other functions or endpoints

- Using '.env.test' for testing

- The get_task_or_403 function is standard when calling for a task. 403 is returned for users trying to access tasks that they don't own. If task can't be found then error 404 is returned.

- Had problems with setting up API endpoints with database and authentication. Steep learning curve. This was my first time using FastAPI. I used Django before so using FastAPI with almost few things built in was a challenge.

- If pre-commit fails, you should re-commit. Linters can find errors and fix them, but if the original version does not pass, you need to re-commit, and then it will work properly. I decided to leave this in as a security measure. Having the pre-commit successfully pass, even if it found an error and corrected it, doesn't seem like best practice. It doesn't seem like best practice because even if pre-commit fixes the error you don't know what the error was. The error could be caused by something serious. For example, a common error is that there is no extra line at the bottom of some pages.
---

## 7. **Running the Application**
Make sure your .env file is set up properly before running
```bash
uvicorn app.main:app --reload
```
or if using Docker
```bash
docker-compose up
```
or you want to run tests in Docker to make sure everything works
```bash
docker-compose run --rm app pytest --cov -v
```
Then enter 'http://127.0.0.1:8000/' in your search bar to access the frontend or 'http://127.0.0.1:8000/docs' to access interactive documentation

---

## 8. **Pre-commit Hooks**

Pre-configured with:

- `ruff`: code linting and auto-fix
- `isort`: import sorting
- `mypy`: static typing
- `bandit`: security checks
- `gitleaks`: secret detection
- `pytest --cov`: with 90% minimum coverage

## Data Models and Schemas Explained

This application uses **SQLAlchemy models** to define database tables and **Pydantic schemas** to ensure proper values and serialize API data.

- **Models** define the structure and relationships of the database components.
- **Schemas** ensure data validation for requests and define the response payloads.

---

### Key Models Example (`app/models/models.py`)

```python
import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


class TaskStatus(str, enum.Enum):  # Defines values for status field in Task model. Enforces exact matches
    new = "New"
    in_progress = "In Progress"
    completed = "Completed"


class User(Base):  # Defines user table in database with corresponding columns and tasks relationship
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(Text, nullable=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="owner", cascade="all, delete")


class Task(Base):  # Defines Task model with ForeignKey to user's id with relationship to user defined. Status defined in TaskStatus.
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.new)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    owner = relationship("User", back_populates="tasks")

```
---

## 9. **API Endpoints**
### Auth Endpoints

```
| Method | Endpoint            | Description              | Unauthenticated access|
|--------|---------------------|--------------------------|-----------------------|
| POST   | `/auth/register`    | Register new user        | True                  |
| POST   | `/auth/login`       | Get JWT token for user   | True                  |
```
Auth endpoints return an access token:
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```
### Task Endpoints
```
| Method | Endpoint                        | Description                      | Unauthenticated access|
|--------|---------------------------------|----------------------------------|-----------------------|
| GET    | `/tasks/public`                 | Get all tasks (public)           | False                 |
| GET    | `/tasks`                        | Get all user’s tasks (private)   | False                 |
| POST   | `/tasks`                        | Create a new task                | False                 |
| GET    | `/tasks/{task_id:int}`          | Get a specific task              | False                 |
| PUT    | `/tasks/{task_id:int}`          | Update a task                    | False                 |
| DELETE | `/tasks/{task_id:int}`          | Delete a task                    | False                 |
| PUT    | `/tasks/{task_id:int}/complete` | Update task status to 'Completed'| False                 |
| GET    | `/tasks/filter-by-status/`      | Filter tasks by status           | False                 |

```



---

## 10. **Security Features**



- Passwords hashed using `bcrypt` via `passlib`
- Tokens signed using `python-jose` with expiry
- SQLAlchemy rollback on DB exceptions
- `bandit` and `gitleaks` to prevent insecure code and secrets

---
## 11. **Running Tests**
All endpoints are thoroughly tested. Tests cover:
- User registration/login
- JWT token handling
- All task CRUD operations
- Status filtering
- Mark-as-complete
- 403 and 404 error handling
- And more

Tests automatically load environment variables from .env.test via pytest.ini
```bash
pytest
```

---

## 12. **Project Structure & Testing**

### Project Directory Structure

```
todo_api/
├── .coverage
├── .coveragerc
├── .dockerignore
├── .env
├── .env.test
├── .gitignore
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes_auth.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── routes_tasks.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── deps.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── models.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_routes.py
│   │   ├── test_routes_auth.py
│   │   ├── test_routes_tasks.py
│   │   ├── test_schemas.py
│   ├── main.py
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── README.md
