# Architecture Guide

## Clean Architecture Overview

This project follows Clean Architecture principles, separating concerns into distinct layers:

### 1. Domain Layer
- Contains business logic
- Independent of external frameworks
- Uses dataclasses for entities
- Example:  ```python
  @dataclass
  class Task:
      id: Optional[int]
      title: str
    ```

### 2. Application Layer
- Orchestrates the flow of data
- Implements use cases
- Example:  ```python
  class TaskService:
      def __init__(self, repository: ITaskRepository):
          self.repository = repository
    ```

### 3. Infrastructure Layer
- Implements interfaces defined in domain
- Handles external dependencies
- Example:  ```python
  class SQLAlchemyTaskRepository(ITaskRepository):
      def __init__(self, session: AsyncSession):
          self.session = session  ```

## Dependency Flow
- Dependencies flow inward
- Domain layer has no external dependencies
- Each layer depends only on the layer below it

## Error Handling
- Use domain-specific exceptions
- Transform to HTTP exceptions at the controller level
- Example:  ```python
  try:
      task = await service.get_task(task_id)
  except TaskNotFoundError as e:
      raise HTTPException(status_code=404, detail=str(e))  ```

## Testing Strategy
- Unit tests for domain logic
- Integration tests for repositories
- End-to-end tests for API endpoints
