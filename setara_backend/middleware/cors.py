def cors_tween_factory(handler, registry):
    """
    A custom tween to handle CORS (Cross-Origin Resource Sharing) headers.
    """
    def cors_tween(request):
        # For pre-flight OPTIONS requests, return a response immediately
        if request.method == 'OPTIONS':
            response = request.response
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response

        # For all other requests, first get the actual response from the view
        response = handler(request)

        # Then, add the CORS headers to the outgoing response
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

        return response

    return cors_tween
