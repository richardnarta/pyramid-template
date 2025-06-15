from setara_backend.models import TblUser


class UserMapper:
    @staticmethod
    def db_to_access_token(user: TblUser):
        try:
            data = {}
            if user:
                data = user.__dict__.copy()

                data['user_status'] = user.user_status.value
                data['user_approved_at'] = data['user_approved_at'].isoformat()
                data['user_updated_at'] = data['user_updated_at'].isoformat()
                data['user_created_at'] = data['user_created_at'].isoformat()
                del data['user_password']
                del data['_sa_instance_state']

            return data
        except Exception as e:
            return {}
