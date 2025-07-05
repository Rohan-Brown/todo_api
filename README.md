# FastAPI ToDo List API
A functioning API based ToDoList application built with PostgreSQL, FastAPI, and Docker. Implemented JWT authentication, registration, CRUD, static templating.

User authentication and registration with JWT
Token-based authentication
Mark as complete
Containerized deployment with docker

Technologies

FastAPI
PostgreSQL
SQLAlchemy
Docker
Uvicorn
Pydantic
JWT Authentication

Requirements

Python 3.12+
Docker

Example .env

DATABASE_URL=postgresql://username:password@host:5432/database_name
SECRET_KEY=key
ALGORITHM=some_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=10

For recruiters
Assuming 6 symbols required the password field means 6 characters and not 6 special characters e.g. @#$

Decided to use TaskStatus model instead of using 'constr' with 'regex' or 'Literal'. Using TaskStatus model for ease of use and because it follows best practice.

Added filter_task_by_status endpoint only because of task requirements. It doesn't appear in the frontend and is not reused in other functions or endpoints
