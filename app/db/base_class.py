import typing as t

from sqlalchemy.ext.declarative import as_declarative, declared_attr


# Create tables and columns based on the Python classes using the ORM. 
# Done via DECLARATIVE MAPPER.
# Common pattern: construct the base class using the SQLAlchemy `declarative_base`
# and have all db model classes inherit from the base class.

class_registry: t.Dict = {}

# In our case, we’re doing the same thing but with a decorator (provided by SQLAlchemy)
# so that we can declare some helper methods on our Base class - like automatically generating a __tablename__.

@as_declarative(class_registry=class_registry)
class Base:
    id: t.Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()