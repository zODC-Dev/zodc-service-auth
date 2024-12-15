# Contributing Guide

## Getting Started

1. Clone the repository
2. Install dependencies:   ```bash
   poetry install   ```
3. Set up pre-commit hooks:   ```bash
   pre-commit install   ```

## Development Workflow

1. Create a new branch:   ```bash
   git checkout -b feature/your-feature   ```

2. Make your changes following our code conventions

3. Write tests for your changes

4. Run tests:   ```bash
   pytest   ```

5. Submit a pull request

## Branch Naming
- Feature: `feature/description`
- Bug fix: `fix/description`
- Refactor: `refactor/description`

## Commit Messages
Follow conventional commits:
```
[ZODC-<Jira task number>]: <meaning full message>
```


## Code Review Process
1. All code must be reviewed
2. Tests must pass
3. Code must follow project conventions
4. Documentation must be updated
