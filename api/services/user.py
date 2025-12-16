from typing import List, Optional

from api.extensions import db
from api.models import UserModel

def get_all_users() -> List[UserModel]:
    return db.session.query(UserModel).all()

def get_user_by_id(user_id: int) -> Optional[UserModel]:
    return db.session.get(UserModel, user_id)