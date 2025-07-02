from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from app.api.routes import router as hello_router
from app.auth.routes_auth import router as auth_router
from app.crud.routes_tasks import router as tasks_router
from app.db.session import engine
from app.models.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
app.include_router(hello_router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/static/login.html")
