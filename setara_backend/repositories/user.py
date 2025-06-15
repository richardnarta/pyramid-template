from sqlalchemy.orm import Session
from sqlalchemy import or_
from setara_backend.models import (
    TblUser,
    UserStatusEnum
)


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_identifier(
        self,
        identifier_type,
        user_identifier,
        user_status=[
            UserStatusEnum.active,
            UserStatusEnum.inactive,
            UserStatusEnum.deleted,
        ],
    ) -> TblUser:
        user = self.session.query(TblUser).filter(
            TblUser.user_status.in_(user_status)
        )

        if identifier_type == 'phone':
            user.filter(TblUser.user_phone == user_identifier)
        elif identifier_type == 'username':
            user.filter(TblUser.user_username == user_identifier)
        elif identifier_type == 'email':
            user.filter(TblUser.user_email == user_identifier)
        else:
            user.filter(TblUser.user_id == user_identifier)

        return user.first()

    def update_user(
        self,
        user: TblUser,
        new_data: dict
    ) -> bool:
        if not user:
            return False

        update_text_field = [
            'user_phone', 'user_username', 'user_name',
            'user_email', 'user_password', 'user_is_verified',
            'user_is_login', 'user_approved_at',
            'user_reject_message', 'user_status',
            'user_approved_by',
        ]

        for field in update_text_field:
            if field in new_data:
                setattr(user, field, new_data.get(field))

        return True
