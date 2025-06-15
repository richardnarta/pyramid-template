from pyramid.view import view_defaults, view_config
from setara_backend.schemas import UserSchema
from setara_backend.handlers.auth import AuthHandler
from . import (
    secure_view,
    validate_form_schema
)


@view_defaults(renderer='json')
class AuthView:
    def __init__(self, request):
        self.request = request
        self.session = self.request.dbsession
        self.auth_handler = AuthHandler(self.session)

    @view_config(route_name='login', renderer='json', request_method='POST')
    @validate_form_schema(UserSchema)
    @secure_view(type='public')
    def login_view(self):
        self.request.response.status = 201

        return self.auth_handler.login_handler(
            self.request
        )

    @view_config(route_name='logout', renderer='json', request_method='GET')
    @secure_view(type='private')
    def logout_view(self):
        self.request.response.status = 200

        return self.auth_handler.logout_handler(
            self.request
        )
