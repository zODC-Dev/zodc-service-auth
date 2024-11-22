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

Or

```bash
alembic upgrade head
```

If you want to downgrade the migrations, run `alembic downgrade -1`.

If you create a new model, please import it in `alembric_migrations/env.py` and add it to the `target_metadata`.

## Swagger

To access the swagger documentation, go to `http://localhost:8000/docs`.
