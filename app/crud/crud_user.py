from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        #Take the form data, extract & encrypt the password
        create_data = obj_in.dict()
        create_data.pop("password")
        db_obj = User(**create_data)
        db_obj.hashed_password = get_password_hash(obj_in.password)
        db.add(db_obj)
        db.commit()

        return db_obj


    def update(self, db: Session, *, db_obj: User, 
        obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:

        # Unnecessary? Already being done by parent (I think)
        # if isinstance(obj_in, dict):
        #     update_data = obj_in
        # else:
        #     update_data = obj_in.dict(exclude_unset=True)
        # return super().update(db, db_obj=db_obj, obj_in=update_data)

        return super().update(db, db_obj=db_obj, obj_in=obj_in)


    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)