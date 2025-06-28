from fastapi import FastAPI

from app.api import routes
from app.auth import routes_auth
from app.crud import routes_tasks
from app.db.session import engine
from app.models.models import Base

app = FastAPI()

app.include_router(routes.router)
app.include_router(routes_tasks.router)
app.include_router(routes_auth.router)

Base.metadata.create_all(bind=engine)
