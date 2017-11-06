import os

# Environment we need to collect.
DATABASE_URL = os.environ.get('DATABASE_URL')

GOOGLE_CLIENT_ID = '148567986475-hjkjihnqn54603235u4rhilh54osclcc.apps.googleusercontent.com'

# This will be used to encrypt short-term cookies
# A random value generated at start should suffice
SECRET_BASE = os.environ.get('SECRET_BASE', os.urandom(64).hex())

# Vancouver stuff.
VANCOUVER_LAT = 49.241
VANCOUVER_LON = -123.1073
VANCOUVER_RAD = "10km"

DEFAULT_LAT = VANCOUVER_LAT
DEFAULT_LON = VANCOUVER_LON
DEFAULT_RAD = VANCOUVER_RAD

# Date params
DATE_FMT = '%Y-%m-%d'
