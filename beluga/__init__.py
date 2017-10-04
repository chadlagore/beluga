from asyncio import AbstractEventLoop

from sanic import Sanic

import beluga.config as config
from beluga.routes import (
    healthcheck,
    get_self, 
    get_event,
    rsvp
)


# Build app and configuration.
app = Sanic()
app.config.from_object(config)

# User routes.
app.add_route(healthcheck, "/", ['GET'])
app.add_route(get_self, "/users/self", ['GET'])


# Event routes.
app.add_route(get_event, "/events", ['GET', ])
app.add_route(rsvp, "/events/<uuid>/rsvp", ['POST', 'DELETE'])
