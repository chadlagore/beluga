import datetime as dt
from datetime import timezone as tz
import math

from asyncio import AbstractEventLoop

from geoalchemy2 import WKTElement

import os

from sanic import Blueprint
from sanic.exceptions import abort
from sanic.response import html, json, redirect

import ujson

from beluga import auth, config
from beluga.models import session_scope, Event
from beluga.auth import authorized
from beluga import config

api = Blueprint('api')

METERS_PER_KILOMETER = 1000.0


# Basic routes.
@api.route('/', ['GET'])
async def healthcheck(request):
    return json({"hello": "async world"})


# User routes.
@api.route('/users/self', ['GET'])
@authorized()
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

@api.route('/sessions', ['POST'])
async def create_session(request):
    """
    @api {post} /sessions Create a new session.
    @apiName CreateSession
    @apiGroup Users

    @apiDescription Create a new session using the specified service.
                    This route should be opened in a web view on the
                    client. A JSON object containing the key `token`
                    will be returned. This token is a bearer token
                    to be used in future API requests.
    
    @apiParam {String} service The service identifier, as described
        in the API documentation.
    @apiParam {String} token The token from the service, used to
        authenticate the user.
    """

    try:
        service = request.json['service']
        service_token = request.json['token']
    except KeyError:
        raise abort(400)

    if service == auth.GOOGLE_SERVICE_ID:
        token = await auth.google(service_token)
    else:
        raise abort(404, "the specified service was not found")

    if token is None:
        raise abort(403)

    return json({ 'token': token })

# Event routes.
@api.route('/events', ['GET'])
@authorized()
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
    @apiParam {Number} [limit] The number of events to return
        (default 50).

    @apiSuccess {Array} results Event objects.
    @apiSuccess {String} next URL of the next page of results.
    @apiSuccess {String} previous URL of the previous page of results.
    """
    start_time = request.args.get('start_time', None)
    end_time = request.args.get('end_time', None)

    # Parse date query.
    if start_time:
        try:
            start_time = dt.datetime.strptime(start_time, config.DATE_FMT)
        except ValueError:
            abort(400, f'start_time ({start_time}) must in format YYYY-MM-DD')
    else:
        start_time = dt.date.min
    
    if end_time:
        try:
            end_time = dt.datetime.strptime(end_time, config.DATE_FMT)
        except ValueError:
            abort(400, f'end_time ({end_time}) must in format YYYY-MM-DD')
    else:
        end_time = dt.date.max

    # TODO: Remove default lat/lon when larger area collected.
    lat = request.args.get('lat', config.DEFAULT_LAT)
    lon = request.args.get('lon', config.DEFAULT_LON)
    radius = request.args.get('radius', config.DEFAULT_RAD.strip('km'))
    limit = request.args.get('limit', 50)

    try:
        dist = float(radius) * METERS_PER_KILOMETER
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        abort(400, 'radius, lat and lon must be numeric')

    try:
        limit = int(limit)
    except ValueError:
        abort(400, f'limit {limit} must be numeric')

    category = request.args.get('category', None)

    # Center point of search area from request.
    center_point = WKTElement(f"POINT({lon} {lat})")
    distance_col = Event.location.ST_Distance(center_point).label('distance')

    with session_scope() as db_session:
        cols = [
            Event.title,
            Event.description_html,
            Event.description_text,
            Event.start_time,
            Event.end_time,
            Event.location.ST_AsGeoJSON().label("location_json"),
            Category.name.label('category'),
            distance_col
        ]

        # Build SQL query.
        event_query = (
            db_session
            .query(*cols)
            .filter(Event.start_time >= start_time)
            .filter(Event.end_time <= end_time)
            .join(Category, Event.category_id == Category.category_id)
            .filter(Event.location.ST_DWithin(center_point, dist))
            .order_by(distance_col.asc())
        )

        if category:
            event_query = event_query.filter(Category.name == category)

        # Format according to API spec, not DB schema
        return json({'results': [{
                'title': e.title,
                'description_html': e.description_html,
                'description_text': e.description_text,
                'location': geojson_to_latlon(e.location_json),
                'start_time': e.start_time.astimezone(tz.utc).isoformat(),
                'end_time': e.end_time.astimezone(tz.utc).isoformat(),
                'distance': e.distance,
                'category': e.category
            } for e in event_query.limit(limit)]})


@api.route('/events/<uuid>/rsvp', ['POST', 'DELETE'])
@authorized()
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


def geojson_to_latlon(geojson):
    """Convert from GeoJSON to API lat/lon format"""
    geo = ujson.loads(geojson)
    assert geo["type"] == "Point"

    return {
        'lat': geo['coordinates'][1],
        'lon': geo['coordinates'][0]
    }


@authorized()
@api.route('/categories', ['GET'])
async def categories_handler(request):
    """
    @api {post} /categories Get event categories.

    @apiDescription Collect available categories.

    @apiName CategoryList
    @apiGroup Categories
    """
    with session_scope() as session:
        return json({
            "results": [
                c.name for c in session.query(Category)
            ]
        })
