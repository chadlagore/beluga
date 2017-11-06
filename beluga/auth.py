import base64

from beluga import config
from beluga.models import session_scope, User

from functools import wraps

from google.oauth2 import id_token, credentials
from google.auth.transport import requests as grequests
import google_auth_oauthlib.flow
import googleapiclient.discovery

from itsdangerous import Signer, BadSignature

from sanic.response import json

import os
import ujson

state_signer = Signer(config.SECRET_BASE)

BEARER_TOKEN_TYPE = 'bearer'
GOOGLE_TOKEN_TYPE = 'google'

GOOGLE_SERVICE_ID = "google"

def authorized():
    """A decorator for authorization.

    Example:

        @app.route("/")
        @authorized()
        async def test(request):
            return json({status: 'authorized'})

    NOTE: This decorator must come after the @api.route decorator
          to take effect.
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
    if os.environ.get("BELUGA_TEST") == "true":
        return True

    # Validate header presence
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False

    # Validate header format
    auth_components = auth_header.split(' ')
    if len(auth_components) != 2:
        return False
    if auth_components[0] != "Bearer":
        return False
    bearer_token = auth_components[1]

    # Validate signature
    try:
        user_id = unsign(BEARER_TOKEN_TYPE, bearer_token)
    except BadSignature:
        return False

    # Validate user exists
    with session_scope() as db_session:
        query = db_session.query(User).filter(User.id == user_id)
        return db_session.query(query.exists()).scalar()

async def google(token):
    """Create a session using a Google OAuth2 token"""
    try:
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), config.GOOGLE_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('bad issuer in token')
    except ValueError or KeyError:
        # Bad token! Bail out!
        return None

    uid = idinfo['sub']
    given_name = idinfo['given_name']
    surname = idinfo['family_name']
    avatar = idinfo['picture']

    with session_scope() as db_session:
        query = db_session.query(User).filter(
            User.login_service == GOOGLE_SERVICE_ID,
            User.login_uid == uid
        )
        
        if db_session.query(query.exists()).scalar():
            user = query.first()
        else:
            user = User(
                given_name=given_name,
                surname=surname,
                avatar=avatar,
                login_service=GOOGLE_SERVICE_ID,
                login_uid=uid,
                login_info=user_info
            )
            db_session.add(user)
            db_session.commit()

        authenticated_user_id = user.id

    # sign a bearer token
    # We should *NOT* use this long term because this scheme
    # only allows us to single a single bearer token value per user
    return sign(BEARER_TOKEN_TYPE, authenticated_user_id)

def sign(sig_type, unsigned):
    """Sign a typed value"""
    encoded_state = ujson.dumps({
        'type': sig_type,
        'val': unsigned
    })
    raw_bytes = bytes(encoded_state, 'utf-8')
    signature = state_signer.sign(raw_bytes)
    return base64.b64encode(signature).decode('ascii')

def unsign(sig_type, signed):
    """Verify a signature and type. Returns signed value"""
    signed_decoded = base64.b64decode(bytes(signed, 'ascii'))
    raw_bytes = state_signer.unsign(signed_decoded)
    state = ujson.loads(raw_bytes.decode('utf-8'))

    if state['type'] != sig_type:
        raise Exception("signature type mismatch")
    
    return state['val']
