from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, constr


class TaskStatus(str, Enum):  # Enforces specific string values
    new = "New"
    in_progress = "In Progress"
    completed = "Completed"


class UserCreate(BaseModel):  # Defines user creation fields
    first_name: str
    last_name: Optional[str] = None
    username: str
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):  # Defines user login fields
    username: str
    password: str


class Token(BaseModel):  # Defines token fields
    access_token: str
    token_type: str



class TaskCreate(BaseModel):  # Defines task creation fields
    title: str = Field(..., min_length=1)
    description: Optional[str] = None


class TaskUpdate(BaseModel):  # Defines task updating fields
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskOut(BaseModel):  # Defines returned task fields
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus

    class Config:
        from_attributes = True

class PaginatedTasks(BaseModel):  # Defines pagination information
    total: int
    skip: int
    limit: int
    tasks: List[TaskOut]
