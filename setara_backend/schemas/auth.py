from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from setara_backend.utils import PHONE_REGEX
from setara_backend.schemas import BaseSchema


class UserSchema(BaseSchema):
    login_method = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['phone', 'username', 'email'],
            error="Login method must be one of: {choices}"
        )
    )
    user_identifier = fields.Str(required=False)
    user_password = fields.Str(
        required=True,
        validate=validate.Regexp(
            regex=r'^(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>])(?=.*\d).{8,}$',
            error="Password harus berjumlah minimal 8 karakter dan memiliki sebuah huruf besar, sebuah angka, dan sebuah simbol."
        )
    )
    user_notification_token = fields.Str(required=True)

    @validates_schema
    def validate_login_credentials(self, data, **kwargs):
        """
        This method is automatically called to validate the entire schema's data.
        It enforces our conditional logic based on the 'login_method'.
        """
        login_method = data.get('login_method')
        identifier = data.get('user_identifier')

        if login_method == 'phone':
            if not PHONE_REGEX.match(identifier):
                raise ValidationError({
                    'user_identifier': [
                        "Format nomor telepon tidak valid. "
                        "Harus dimulai dengan +62 dan memiliki 9-13 digit."
                    ]
                })

        elif login_method == 'email':
            try:
                validate.Email()(identifier)
            except ValidationError:
                raise ValidationError({
                    'user_identifier': ["Email tidak valid."]
                })

        elif login_method == 'username':
            if len(identifier) < 3:
                raise ValidationError({
                    'user_identifier': ["Username must be at least 3 characters long."]
                })
