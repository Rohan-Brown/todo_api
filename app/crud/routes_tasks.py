from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.deps import get_current_user, get_db
from app.models.models import Task, TaskStatus, User
from app.schemas.schemas import PaginatedTasks, TaskCreate, TaskOut, TaskUpdate

router = APIRouter()



@router.get("/public", response_model=PaginatedTasks)
def get_all_tasks(  # Returns paginated queried tasks created by anyone
    status: Optional[TaskStatus] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Not used. Only to restrict access to authenticated users
):
    query = db.query(Task)
    if status:
        query = query.filter(Task.status == status)

    total = query.count()
    tasks = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "tasks": tasks
    }


@router.get("", response_model=PaginatedTasks)
def get_all_user_tasks(  # Returns paginated queried tasks created by current user only.
    status: Optional[TaskStatus] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Task).filter(Task.user_id == current_user.id)
    if status:
        query = query.filter(Task.status == status)

    total = query.count()
    tasks = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "tasks": tasks
    }

@router.get("/{task_id:int}", response_model=TaskOut)
def get_specific_task(  # Returns details to a specific task only if created by current user
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (  # Only returns task if created by current user
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("", response_model=TaskOut)
def create_task(  # Creates task based on TaskCreate schema
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_task = Task(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.put("/{task_id:int}", response_model=TaskOut)
def update_task(  # Updates task based on TaskUpdate schema only if task was created by current user
    task_id: int,
    updates: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id:int}")
def delete_task(  # Deletes task only if task was created by current user
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}


@router.post("/{task_id:int}/complete", response_model=TaskOut)
def mark_completed(  # Marks task as complete although update_task updates the task to be New, In Progress or Complete
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskStatus.completed
    db.commit()
    db.refresh(task)
    return task

@router.get("/filter-by-status/", response_model=PaginatedTasks)
def filter_task_by_status(  # Filters query by status although filter by status already implemented in get_all_tasks and get_all_user_tasks
    status: Optional[TaskStatus] = Query(None, description="Filter tasks by status"),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Not used. Only to restrict access to authenticated users
):
    query = db.query(Task)

    if status is not None:
        query = query.filter(Task.status == status)

    total = query.count()
    tasks = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "tasks": tasks
    }
