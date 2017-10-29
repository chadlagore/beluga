import os


# Environment we need to collect.
DATABASE_URL = os.environ.get('DATABASE_URL')

# Vancouver stuff.
VANCOUVER_LAT = 49.241
VANCOUVER_LON = -123.1073
VANCOUVER_RAD = "10km"

DEFAULT_LAT = VANCOUVER_LAT
DEFAULT_LON = VANCOUVER_LON
DEFAULT_RAD = VANCOUVER_RAD

# Date params
DATE_FMT = '%Y-%m-%d'