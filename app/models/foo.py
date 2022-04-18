from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Foo(Base):
    id = Column(Integer, primary_key=True, index=True)
    col1 = Column(String(256), nullable=True)
    col2 = Column(String(256), nullable=True)
    col3 = Column(String, index=True, nullable=False)
