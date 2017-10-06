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
    raise NotFound('event_handler not implemented')


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
    raise NotFound('rsvp_handler not implemented')


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
