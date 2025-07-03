from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
def say_hello():  # For testing if routing is functioning
    return {"message": "Hello and welcome to my TaskListApp!"}
