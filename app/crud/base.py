from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


# Models inheriting from CRUDBase will be defined with a SQLAlchemy model 
# as the first argument, then the Pydantic model (aka schema) for creating 
# and updating rows as the second and third arguments

# https://www.youtube.com/watch?v=yScuF1UgGU0
# Generic[ModelType, CreateSchemaType, UpdateSchemaType]
# Basically means (below): "I'm going to instantiate this class and its going
# to be with one of these three "

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model


    def add_and_refresh(self, db: Session, db_obj: Any) -> None:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)


    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()


    def get_multi(self, db: Session, *, skip: int = 0, 
        limit: int = 100) -> List[ModelType]:

        return db.query(self.model).offset(skip).limit(limit).all()


    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:

        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        # db.add(db_obj)
        # db.commit()
        # db.refresh(db_obj)
        self.add_and_refresh(db=db, db_obj=db_obj)
        return db_obj


    def update(self, db: Session, *, db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:

        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        # db.add(db_obj)
        # db.commit()
        # db.refresh(db_obj)
        self.add_and_refresh(db=db, db_obj=db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj