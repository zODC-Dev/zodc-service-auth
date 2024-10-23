# zODC Backend

This is the backend for the zODC project.

## Start the server

```bash
poetry shell
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Database

To create a new migration, run `alembic revision --autogenerate -m "migration_name"`.

To apply the migrations, run `python -m src.scripts.run_migrations`.

