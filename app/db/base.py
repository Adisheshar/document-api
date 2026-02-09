#app/db/base
from sqlalchemy.orm import DeclarativeBase

# Shared declarative base for all SQLAlchemy ORM models
class Base(DeclarativeBase):
    pass
