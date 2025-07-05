from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.deps import get_current_user, get_db
from app.models.models import Task, TaskStatus, User
from app.schemas.schemas import PaginatedTasks, TaskCreate, TaskOut, TaskUpdate

router = APIRouter()

"""
'filter_task_by_status' and 'mark_completed' only exist because it was specified in task requirements. Read more about
it in README file.
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
    """
    Retrieve a paginated list of all tasks created by any user.

    Args:
        status (Optional[TaskStatus]): Optional filter to return tasks with the status given.
        skip (int): Number of tasks to skip
        limit (int): Maximum number of tasks to return.
        db (Session): SQLAlchemy database session (dependency injection).
        current_user (User): Currently authenticated user (to manage access to endpoints for authenticated users only).

    Returns:
        PaginatedTasks: A dictionary with keys 'total', 'skip', 'limit', and 'tasks'. Contains the paginated results

    Notes:
        - Returns tasks created by any user (not just the current user).
        - `current_user` is used only to enforce authentication. No active use
        - Supports optional filtering with task status.
    """
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
    """
    Retrieve a paginated list of all tasks created by the current user.

    Args:
        status (Optional[TaskStatus]): Optional filter to return tasks with the status given.
        skip (int): Number of tasks to skip
        limit (int): Maximum number of tasks to return.
        db (Session): SQLAlchemy database session (dependency injection).
        current_user (User): Currently authenticated user (to manage access to endpoints for authenticated users only).

    Returns:
        PaginatedTasks: A dictionary with keys 'total', 'skip', 'limit', and 'tasks'. Contains the paginated results

    Notes:
        - Returns tasks created by the current user.
        - Supports optional filtering with task status.
    """
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
    """
    Retrieves a specific task created by the current user.

    Args:
        task_id (int):  Identifies the specific task to return
        db (Session): SQLAlchemy database session (dependency injection).
        current_user (User): Currently authenticated user (to manage access to endpoints for authenticated users only).

    Returns:
        TaskOut: A Pydantic model representing the requested information.

    Raises:
        HTTPException 403: If the task does not belong to the current user.
        HTTPException 404: If the task with the given ID does not exist.

    Notes:
        - Only the user who created the task can access it
        - Returns specific task created by the current user.
    """
    task = get_task_or_403(task_id, current_user.id, db)  # Only returns task if created by current user
    return task

@router.post("", response_model=TaskOut)
def create_task(  # Creates task based on TaskCreate schema
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a task with schema TaskCreate for the current user.

    Args:
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated user making the request.

    Raises:
        HTTPException 500: If there is a database error which will cause the task to not be created because of rollback.

    Returns:
        TaskOut: A Pydantic model representing the requested information.
    Notes:
        - Authentication is enforced: only authenticated users can create tasks.
        - The task is connected to the user creating it.

    """
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
    """
    Updates a task with the schema TaskUpdate for the current user if they are authorized to access this task.

    Args:
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated user making the request.

    Returns:
        TaskOut: A Pydantic model representing the requested information.

    Raises:
        HTTPException 403: If the task does not belong to the current user.
        HTTPException 404: If the task with the given ID does not exist.
        HTTPException 500: If there is a database error which will cause the task to not be updated because of rollback.


    Notes:
        - Authentication is enforced: only authenticated users can create tasks.
        - Tasks with empty titles will fail
    """
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
    """
    Deletes a task for the current user if they are authenticated.

    Args:
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated user making the request.

    Returns:
        dict: {"message": "Task deleted"}

    Raises:
        HTTPException 403: If the task does not belong to the current user.
        HTTPException 404: If the task with the given ID does not exist.
        HTTPException 500: If there is a database error which will cause the task to not be deleted because of rollback.


    Notes:
        - Authentication is enforced: only authenticated users can delete tasks.
        - Users can only delete their own tasks
    """
    task = get_task_or_403(task_id, current_user.id, db)
    try:
        db.delete(task)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete task")
    return {"message": "Task deleted"}


@router.put("/{task_id:int}/complete", response_model=TaskOut)
def mark_completed(  # Marks task as Completed although update_task updates the task to be New, In Progress or Completed
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Set a specific task's status to "Completed" only if the task belongs to the current user.

    Args:
        task_id (int): ID of the task to mark as completed.
        db (Session): SQLAlchemy database session.
        current_user (User): The user attempting to update task.

    Returns:
        TaskOut: The updated task with its status set to 'Completed'.

    Raises:
        HTTPException 403: If the task does not belong to the current user.
        HTTPException 404: If the task does not exist.
        HTTPException 500: If the database update fails.

    Notes:
        - Only the owner of the task can mark it as 'Completed'.
        - Redundant because status updating is already supported by `update_task`.
        - Could be used as shortcut instead of using `update_task`.

    """
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
    """
    Retrieve a paginated list of tasks that are filtered by status.

    Args:
        status (Optional[TaskStatus]): Filter tasks by their status (e.g., New, In Progress, Completed).
        skip (int): Number of tasks to skip.
        limit (int): Maximum number of tasks to return.
        db (Session): SQLAlchemy database session.
        current_user (User): Authenticated user (used to enforce authentication only).

    Returns:
        PaginatedTasks: A dictionary with keys 'total', 'limit', 'skip', and 'tasks' containing the filtered paginated results.

    Notes:
        - This endpoint returns tasks created by any user, not just the current one.
        - Authentication is required even though current_user isn't used in function.
        - Redundant because status filtering is already supported by `get_all_tasks` and `get_specific_task`.
    """
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
