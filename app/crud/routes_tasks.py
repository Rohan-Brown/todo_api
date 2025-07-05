from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.deps import get_current_user, get_db
from app.models.models import Task, TaskStatus, User
from app.schemas.schemas import PaginatedTasks, TaskCreate, TaskOut, TaskUpdate

router = APIRouter()

"""
"/tasks/filter-by-status/" only exist because it was specified in task requirements. Read more about it in README file.
"""

def get_task_or_403(task_id: int, user_id: int, db: Session) -> Task:
    # Returns 404 if page not found and 403 if user doesn't have access
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
    return task

@router.get("/public", response_model=PaginatedTasks)
def get_all_tasks(  # Returns paginated queried tasks created by anyone
    status: Optional[TaskStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
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
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
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
    task = get_task_or_403(task_id, current_user.id, db)  # Only returns task if created by current user
    return task

@router.post("", response_model=TaskOut)
def create_task(  # Creates task based on TaskCreate schema
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_task = Task(**task.dict(), user_id=current_user.id)
    db.add(db_task)
    try:
        db.commit()
        db.refresh(db_task)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create task")
    return db_task


@router.put("/{task_id:int}", response_model=TaskOut)
def update_task(  # Updates task based on TaskUpdate schema only if task was created by current user
    task_id: int,
    updates: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    task = get_task_or_403(task_id, current_user.id, db)
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    try:
        db.commit()
        db.refresh(task)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update task")
    return task


@router.delete("/{task_id:int}")
def delete_task(  # Deletes task only if task was created by current user
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    task = get_task_or_403(task_id, current_user.id, db)
    try:
        db.delete(task)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete task")
    return {"message": "Task deleted"}


@router.put("/{task_id:int}/complete", response_model=TaskOut)
def mark_completed(  # Marks task as complete although update_task updates the task to be New, In Progress or Complete
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task_or_403(task_id, current_user.id, db)
    task.status = TaskStatus.completed
    try:
        db.commit()
        db.refresh(task)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to complete task")
    return task

@router.get("/filter-by-status/", response_model=PaginatedTasks)
def filter_task_by_status(  # Filters query by status although filter by status already implemented in get_all_tasks and get_all_user_tasks
    status: Optional[TaskStatus] = Query(None, description="Filter tasks by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
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
