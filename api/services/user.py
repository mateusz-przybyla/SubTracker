from typing import List

from api.models import UserModel

def get_all_users() -> List[UserModel]:
    return UserModel.query.all()