from aiohttp import web
from routes import setup_routes


# Create the application.
app = web.Application()

# Setup our routes.
setup_routes(app)

# Run the app.
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=80)
