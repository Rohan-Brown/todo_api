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
