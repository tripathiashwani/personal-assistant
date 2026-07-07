"""
Declarative base for all ORM models.

Alembic's `env.py` imports `Base.metadata` from this module for
autogenerate support. Every model file must import `Base` from here
(never create a second Base), and every new model module must be
imported in `import_all_models()` below so Alembic can see it —
even though the model itself isn't used directly in this file.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def import_all_models() -> None:
    """
    Ensures every model module is imported at least once, so its table
    is registered on Base.metadata before Alembic autogenerate runs.
    Each new model file gets a line added here.
    """
    from app.models import user  # noqa: F401
    from app.models import document  # noqa: F401
