from asyncio import AbstractEventLoop

from sanic import Blueprint
from sanic.exceptions import abort
from sanic.response import json

from beluga.auth import authorized

api = Blueprint('api')


# Basic routes.
@api.route('/', ['GET'])
async def healthcheck(request):
    return json({"hello": "async world"})


# User routes.
@authorized()
@api.route('/users/self', ['GET'])
async def get_self(request):
    """
    @api {get} /users/self Retrieve the currently logged in user.
    @apiName Self
    @apiGroup Users

    @apiSuccess {String} given_name Firstname of the User.
    @apiSuccess {String} surname Lastname of the User.
    @apiSuccess {Array} logins A list of logins associated with
        the user.
    @apiSuccess {String} avatar A URL to an avatar image.
    """
    raise abort(501, 'not implemented')


# Event routes.
@authorized()
@api.route('/events', ['GET'])
async def event_handler(request):
    """
    @api {get} /events Retrieve a listing of events.
    @apiName Events
    @apiGroup Events

    @apiDescription By default, this endpoint returns events ordered
                    by start time, with events in the past omitted.
                    Events may be filtered by search area, temporal
                    range, or both. Note that if a search area or temporal
                    range parameter is specified, all other parameters of
                    the corresponding class must be provided (i.e. a search
                    area or temporal range must be fully specified).

    @apiParam {Number} lat Latitude component of the coordinates of
        the center of the search area..
    @apiParam {Number} lon Longitude component of the coordinates of
        the center of the search area.
    @apiParam {Number} radius The radius of the search area in
        kilometres.
    @apiParam {Number} start_time The start of the temporal range,
        in RFC 3339 format.
    @apiParam {Number} end_time The end of the temporal range,
        in RFC 3339 format.

    @apiSuccess {Array} results Event objects.
    @apiSuccess {String} next URL of the next page of results.
    @apiSuccess {String} previous URL of the previous page of results.
    """

    from beluga import db_session
    from beluga.models import Event
    
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    radius = request.args.get('radius')

    # Acquire the events the user requested
    if start_time or end_time:
        # Temporal range must be fully specified!
        if not start_time or not end_time:
            raise abort(400, "temporal range must be fully specified")
        
    elif lat or lon or radius:
        if not lat or not lon or not radius:
            raise abort(400, "search area must be fully specified")
    else:
        events = db_session.query(Event).order_by(Event.start_time.desc())

    results = map(lambda event: {
        'title': event.title,
        'location': event.location, # not validating outgoing schema here
        'start_time': event.start_time,
        'end_time': event.end_time
        # No next/previous pages on this one because we're returning everything
    }, events)

    return json({'results': results})


@authorized()
@api.route('/events/<uuid>/rsvp', ['POST', 'DELETE'])
async def rsvp_handler(request, uuid):
    """
    @api {post} /events/:uuid/rsvp RSVP to an event.

    @apiDescription Make this user become an attendee of the event specified
                    by `uuid`. This endpoint does not accept a request body,
                    and does not produce any content. This operation is
                    idempotent.

    @apiName PostRSVP
    @apiGroup Events

    @apiParam {Number} uuid Event unique ID.
    """
    """
    @api {delete} /events/:uuid/rsvp Clear an RSVP to an event.

    @apiDescription Remove this user as an attendee of the event specified by
                    `uuid`. This endpoint does not accept a request body,
                    and does not produce any content. This operation is
                    idempotent.


    @apiName DeleteRSVP
    @apiGroup Events

    @apiParam {Number} uuid Event unique ID.
    """
    raise abort(501, 'not implemented')


# Helper functions
async def delete_rsvp(token, uuid):
    """DELETE RSVP handler.
    Sets the authorized user's RSVP status
    on the event specified by `uuid` to False.
    """
    pass


async def post_rsvp(token, uuid):
    """POST RSVP handler.
    Sets the authorized user's RSVP status
    on the event specified by `uuid` to True.
    """
    pass
