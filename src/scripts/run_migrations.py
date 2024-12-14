import asyncio

from alembic import command
from alembic.config import Config


async def run_migrations() -> None:
    """Run database migrations."""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    asyncio.run(run_migrations())
