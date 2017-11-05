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

    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    radius = request.args.get('radius')
    limit = request.args.get('limit', 50)

    # Validate the parameters we got, if any
    if start_time or end_time:
        if not start_time or not end_time:
            raise abort(400, "temporal range must be fully specified")

    if lat or lon or radius:
        if not lat or not lon:
            raise abort(400, "search area must be fully specified")
        if not radius:
            radius = 10

    # Acquire the events the user requested
    with session_scope() as db_session:
        event_query = db_session.query(
            Event.title,
            Event.description_html,
            Event.description_text,
            Event.start_time,
            Event.end_time,
            Event.location.ST_AsGeoJSON().label("location_json")
        )

        if start_time:
            event_query = event_query.filter(Event.start_time >= start_time)
            event_query = event_query.filter(Event.end_time <= end_time)

        if lat:
            # Center point of search area from request
            center_point = WKTElement("POINT({} {})".format(lon, lat))

            # Apply the filter the user gave us
            event_query = event_query.filter(
                Event.location.ST_DWithin(
                    center_point,
                    (float(radius) * METERS_PER_KILOMETER) # Convert from km to m
                )
            )

            # Add and sort by distance
            distance_col = Event.location.ST_Distance(center_point).label('distance')
            event_query = event_query.add_column(distance_col).order_by(distance_col.asc())
        else:
            # If we didn't get a center point, sort by start time
            event_query = event_query.order_by(Event.start_time.asc())

        # Apply limit.
        event_query = event_query.limit(limit)

        # Format according to API spec, not DB schema
        events = map(lambda event: {
            'title': event.title,
            'description_html': event.description_html,
            'description_text': event.description_text,
            'location': geojson_to_latlon(event.location_json),
            'start_time': event.start_time.astimezone(tz.utc).isoformat(),
            'end_time': event.end_time.astimezone(tz.utc).isoformat(),
            'distance': (event.distance if lat else None)
        }, event_query)

    # No next/previous pages on this one because we're returning everything
    return json({'results': events})


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
