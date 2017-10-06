from asyncio import AbstractEventLoop

from sanic.exceptions import NotFound
from sanic.response import json

from beluga.auth import authorized


# Basic routes.
async def healthcheck(request):
    return json({"hello": "async world"})


# User routes.
@authorized()
async def get_self(request):
    """
    @api {get} /user/self Retrieve the currently logged in user.
    @apiName Self
    @apiGroup Users

    @apiSuccess {String} given_name Firstname of the User.
    @apiSuccess {String} surname Lastname of the User.
    @apiSuccess {Array} logins A list of logins associated with
        the user.
    @apiSuccess {String} avatar A URL to an avatar image.
    """
    raise NotFound('get_self not implemented')


# Event routes.
@authorized()
async def event_handler(request):
    """
    @api {get} /events Retrieve a listing of events.
    @apiName Events
    @apiGroup Events

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
    raise NotFound('event_handler not implemented')


@authorized()
async def rsvp_handler(request, uuid):
    """
    @api {get} /events/:uuid/rsvp RSVP to an event (i.e. become an attendee).
    @apiName RSVP
    @apiGroup Events

    @apiParam {Number} uuid Users unique ID.
    """
    raise NotFound('rsvp_handler not implemented')


# Helper functions
async def delete_rsvp(token, uuid):
    """DELETE RSVP handler.
    Sets the authorized user's RSVP status
    on the event specified by `uuid` to False.
    """
    pass


async def post_rsvp(token, uuid):
    """DELETE RSVP handler.
    Sets the authorized user's RSVP status
    on the event specified by `uuid` to True.
    """
    pass
