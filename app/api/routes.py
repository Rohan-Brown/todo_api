from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
def say_hello():
    return {"message": "Hello and welcome to my TaskListApp!"}
