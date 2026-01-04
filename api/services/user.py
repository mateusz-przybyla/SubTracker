from typing import List

from api.extensions import db
from api.models import UserModel
from api.exceptions import UserNotFoundError

def get_all_users() -> List[UserModel]:
    return db.session.query(UserModel).all()

def get_user_by_id(user_id: int) -> UserModel:
    user = db.session.get(UserModel, user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return user