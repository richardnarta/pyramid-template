from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPForbidden,
    HTTPUnauthorized,
    HTTPBadRequest
)


@view_config(context=HTTPNotFound, renderer='json')
def notfound_view(exc, request):
    request.response.status_code = exc.status_code
    if str(exc).startswith('/'):
        message = f"Endpoint not found: The path '{request.path}' does not exist on this server."
    else:
        message = str(exc) or "The requested resource could not be found."
    return {"error": True, "message": message}


@view_config(context=HTTPForbidden, renderer='json')
def forbidden_view(exc, request):
    request.response.status_code = exc.status_code
    message = str(exc) or "You do not have permission to access this resource."
    return {"error": True, "message": message}


@view_config(context=HTTPUnauthorized, renderer='json')
def unauthorized_view(exc, request):
    request.response.status_code = exc.status_code
    message = str(exc) or "Authentication is required to access this resource."
    return {"error": True, "message": message}


@view_config(context=HTTPBadRequest, renderer='json')
def bad_request_view(exc, request):
    request.response.status_code = exc.status_code

    message = str(
        exc) or "The request was malformed or contained invalid data."
    return {"error": True, "message": message}
