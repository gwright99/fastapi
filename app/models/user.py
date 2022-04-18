from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(256), nullable=True)
    surname = Column(String(256), nullable=True)
    email = Column(String, index=True, nullable=False)
    is_superuser = Column(Boolean, default=False)
    # `nullable=False` causes errors when trying to migrate with Alembic
    # sqlite3.OperationalError: Cannot add a NOT NULL column with default value NULL
    # Seems due to table pre-existing
    # as per Miguael Grinberg, set nullable=True and default to blank string.
    # Seems hacky but trying.
    # https://github.com/miguelgrinberg/Flask-Migrate/issues/81
    # BREAKS
    # hashed_password = Column(String, nullable=False, default=False)
    # BREAKS
    # hashed_password = Column(String, nullable=False, default="")
    # WORKS
    hashed_password = Column(String, nullable=True, default="")
    
    recipes = relationship(
        "Recipe",
        cascade="all,delete-orphan",
        back_populates="submitter",
        uselist=True,
    )