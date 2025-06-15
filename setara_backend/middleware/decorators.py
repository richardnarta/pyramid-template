from functools import wraps
from pyramid.httpexceptions import HTTPUnauthorized, HTTPForbidden, HTTPBadRequest, HTTPUnsupportedMediaType
from marshmallow import ValidationError


def secure_view(type='private', roles=None):
    """
    A decorator to handle view security for authentication and authorization.

    :param type: 'private' (default) or 'public'.
                - 'private': Requires a valid JWT.
                - 'public': No authentication needed.
    :param roles: A list of roles that are allowed to access this view.
                If None or empty, any authenticated user is allowed.
                e.g., ['admin', 'manager']
    """
    def decorator(wrapped_view):
        @wraps(wrapped_view)
        def wrapper(view_instance_or_request, *args, **kwargs):

            if hasattr(view_instance_or_request, 'request'):
                request = view_instance_or_request.request
            else:
                request = view_instance_or_request

            # 1. Handle public routes
            if type == 'public':
                pass
            else:
                # 2. Handle private routes: Check for authentication
                # request.identity is set by our JWTAuthenticationPolicy if the token is valid
                if request.user is None:
                    raise HTTPUnauthorized('missing/invalid token')

                # 3. Handle role-based authorization
                if roles:
                    if request.user['user_role'] not in roles:
                        raise HTTPForbidden()

            return wrapped_view(view_instance_or_request, *args, **kwargs)
        return wrapper
    return decorator


def validate_form_schema(schema_class):
    """
    A decorator to validate incoming multipart/form-data against a Marshmallow schema.
    """
    def decorator(wrapped_view):
        @wraps(wrapped_view)
        def wrapper(view_instance_or_request, *args, **kwargs):
            """
            This wrapper contains the validation logic.
            It runs before the actual view is called.
            """

            if hasattr(view_instance_or_request, 'request'):
                request = view_instance_or_request.request
            else:
                request = view_instance_or_request

            try:
                if not hasattr(request.POST, 'mixed'):
                    form_data = request.POST
                else:
                    form_data = request.POST.mixed()  # pragma: no cover

                if not form_data:
                    raise HTTPUnsupportedMediaType(
                        json_body={
                            "error": True,
                            "message": "only support multipart/form-data"
                        }
                    )

                schema = schema_class()
                validated_data = schema.load(form_data)
                request.validated = validated_data

            except ValidationError as err:
                raise HTTPBadRequest(err.messages)

            return wrapped_view(view_instance_or_request, *args, **kwargs)
        return wrapper
    return decorator
