from functools import wraps
from sanic.response import json


def authorized():
    """A decorator for authorization.

    Example:

        @app.route("/")
        @authorized()
        async def test(request):
            return json({status: 'authorized'})
    """
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):

            # Check for authorization.
            if check_request_for_auth_status(request):
                response = await f(request, *args, **kwargs)
                return response

            else:
                return json({'status': 'not_authorized'}, 403)

        return decorated_function
    return decorator


def check_request_for_auth_status(request):
    """Checks a request to see if the user is authenticated.
    This would likely check for a Bearer token.

    Args:
        request: the request from the client.
    """
    return True  # surrre you are.
