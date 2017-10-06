from sanic import Sanic

import beluga.config as config
from beluga.routes import api


# Build app and configuration.
app = Sanic()
app.config.from_object(config)

# Add routes.
app.blueprint(api)
