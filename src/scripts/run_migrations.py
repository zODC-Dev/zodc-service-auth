import asyncio
from alembic.config import Config
from alembic_migrations import command

async def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    asyncio.run(run_migrations())