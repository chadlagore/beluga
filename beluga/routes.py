import datetime as dt

from sanic import Blueprint
from sanic.exceptions import abort
from sanic.response import json
import sqlalchemy as sa
from sqlalchemy.sql.expression import type_coerce
from geoalchemy2 import func, WKTElement

from beluga.auth import authorized
from beluga.models import Event, session_scope


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
                    by distance from centroid of search area, with
                    events in the past omitted. Events may be
                    filtered by search area, temporal
                    range, or both. Note that if a search area or temporal
                    range parameter is specified, all other parameters of
                    the corresponding class must be provided (i.e. a search
                    area or temporal range must be fully specified).

    @apiParam {Number} lat Latitude component of the coordinates of
        the center of the search area.
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
    # TODO: Error handling.
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    radius = request.args.get('radius')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    lat = 49.241
    lon = -123.1073
    rad = 10000
    start_time = dt.datetime(2017, 1, 1, 0, 0)
    start_time = dt.datetime(2017, 12, 12, 0, 0)

    # Centroid of the request.
    centroid = WKTElement('POINT({} {})'.format(lat, lon), srid=4326)

    # Distance to the centroid.
    distance = Event.location.ST_Distance(centroid).label('distance')
    
    # Cols to query for.
    query_cols = [Event.title, Event.location, distance]

    # Filter for radius.
    within_radius = func.ST_DWithin(Event.location, centroid, radius)

    # TODO: Abstract this out into an EventQuery.
    with session_scope() as db_session:
        query = (
            db_session.query(**query_cols)
                      .filter(within_radius)
                      .filter(Event.start_time >= start_time)
                      .filter(Event.start_time <= end_time)
                      .sort_by(distance)
        )

        results = query.all()

        # TODO: Paginate results
        return json(
            {
                "results": results,
                "next": "",
                "prev": ""
            }
        )


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
