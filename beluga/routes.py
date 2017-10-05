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
    raise NotFound('get_self not implemented')


# Event routes.
@authorized()
async def event_handler(request):
    raise NotFound('event_handler not implemented')


@authorized()
async def rsvp_handler(request, uuid):
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
