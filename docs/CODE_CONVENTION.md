# Code Convention Guide

## Table of Contents
- [Project Structure](#project-structure)
- [Naming Conventions](#naming-conventions)
- [Type Hints](#type-hints)
- [Documentation](#documentation)
- [Error Handling](#error-handling)

## Project Structure
src/
├── domain/ # Business logic and rules
├── infrastructure/ # External implementations
└── app/ # Application layer



## Naming Conventions

### Files
- Use snake_case for all files
- Add appropriate suffixes: `_repository.py`, `_service.py`, `_controller.py`
- Examples:
  ```
  task_repository.py
  task_service.py
  task_controller.py
  ```

### Classes
- Use PascalCase for class names
- Add appropriate prefixes/suffixes based on the layer
- Examples:
  ```python
  class Task:  # Domain entity
  class TaskService:  # Application service
  class SQLAlchemyTaskRepository:  # Infrastructure implementation
  ```

### Methods
- Use snake_case for method names
- Use async prefix for asynchronous methods
- Examples:
  ```python
  async def create_task()
  async def get_task_by_id()
  def validate_task_data()
  ```

## Type Hints
- Always use type hints for method arguments and return types
- Use Optional[] for nullable values
- Examples:
  ```python
  def create_task(self, task: TaskCreate) -> Task:
      pass

  async def get_task(self, task_id: int) -> Optional[Task]:
      pass
  ```

## Documentation
- Use docstrings for classes and public methods
- Follow Google style docstring format
- Example:
  ```python
  def create_task(self, task: TaskCreate) -> Task:
      """Creates a new task.

      Args:
          task: The task creation data.

      Returns:
          The created task entity.

      Raises:
          TaskValidationError: If task data is invalid.
      """
      pass
  ```
