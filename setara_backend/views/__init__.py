from pyramid.view import view_config
from ..middleware.decorators import (
    secure_view,
    validate_form_schema
)


@view_config(route_name='home', renderer='json', request_method='GET')
@secure_view(type='public')
def landing_view(request):
    return {
        "project": "B2B Setara Commodity API",
        "owner": "PT. Arga Bumi Indonesia",
        "version": "2.0.0",
        "docs": "api-stg.b2bsetara.co.id/docs/"
    }
