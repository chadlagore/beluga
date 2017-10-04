from asyncio import AbstractEventLoop

from sanic.exceptions import NotFound
from sanic.response import json

from beluga.auth import authorized


# Basic routes.
async def healthcheck(request):
    return json({"hello": "async worldiasdasd"})


# User routes.
@authorized()
async def get_self(request):
    raise NotFound('not implemented')


# Event routes.
@authorized()
async def get_event(request):
    raise NotFound('not implemented')


@authorized()
async def rsvp(request, uuid):
    success = await delete_rsvp_handler(request, uuid)
    return json({"rsvp_deleted": deleted})


async def delete_rsvp_handler(request, uuid):
    """
    DELETE RSVP handler.
    Sets the authorized user's RSVP status
    on the event specified by `uuid` to False.
    """
    # stub
    return {'deleted': True}


async def post_rsvp_handler(uuid):
    """
    DELETE RSVP handler.
    Sets the authorized user's RSVP status
    on the event specified by `uuid` to True.
    """
    return {'rsvped': True}
