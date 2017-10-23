from datetime import timezone as tz
import math

from sanic import Blueprint
from sanic.exceptions import abort
from sanic.response import json

from beluga.models import session_scope, Event
from beluga.auth import authorized

api = Blueprint('api')

RADIUS_OF_EARTH = 6371.0 # in kilometres


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

    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    radius = request.args.get('radius')

    # Validate the parameters we got, if any
    if start_time or end_time:
        if not start_time or not end_time:
            raise abort(400, "temporal range must be fully specified")

    if lat or lon or radius:
        if not lat or not lon or not radius:
            raise abort(400, "search area must be fully specified")
    
    # Acquire the events the user requested
    with session_scope() as db_session:
        events = db_session.query(Event)
        if start_time:
            events = events.filter(Event.start_time >= start_time)
            events = events.filter(Event.end_time <= end_time)
        if lat:
            # Convert from lat/lon/radius to upper/lower bounds for lat/lon

            # We need to find the length of one degree longitude at the
            # center point we were given. To do so, we take the cosine
            # of the latitude we are given and multiply that by the length
            # of one degree longitude at the equator.
            lat_rads = (math.pi * float(lat)) / 180.0 # given lat in radians
            lon_factor = 1.0 / ((math.pi / 180.0) * RADIUS_OF_EARTH * math.cos(lat_rads))

            # Using an approximation here for simplicity.
            # The distance of a single degree of latitude varies around
            # the globe, but does not vary as dramatically as longitude.
            # We therefore can use an approximation here. More info at
            # https://en.wikipedia.org/wiki/Latitude#Length_of_a_degree_of_latitude.
            lat_factor = 1.0 / 111.0 # 1 deg lat ~= 111 km (give or take 1 km)

            min_lon = float(lon) - (float(radius) * lon_factor)
            max_lon = float(lon) + (float(radius) * lon_factor)

            min_lat = float(lat) - (float(radius) * lat_factor)
            max_lat = float(lat) + (float(radius) * lat_factor)

            # TODO once we can query by location, the query
            # should be modified here to reflect the location we 
            # got from the client.
            pass

    # Sort by start_time for now.
    events = events.order_by(Event.start_time.asc())

    # No next/previous pages on this one because we're returning everything
    return json({'results': [i.as_dict() for i in events.all()]})


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
