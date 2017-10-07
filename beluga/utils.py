import urllib


def parse_database_url(url):
    """
    Parses a database url and returns a dictionary of values:
        {
            'HOST': <YOUR_HOST>,
            'PORT': <YOUR_PORT>,
            'USERNAME': <YOUR_USERNAME>,
            'PASSWORD': <YOUR_PASSWORD>,
            'DATABASE': <YOUR_DATABASE_NAME>,
            'FULLPATH': '/'<YOUR_DATABASE_NAME>
        }

    """
    if not url:
        return {}

    # Parse the URL
    parsed = urllib.parse.urlparse(url)

    # Build the output
    output = dict(
        HOST=parsed.hostname,
        PORT=str(parsed.port),
        USERNAME=parsed.username,
        PASSWORD=parsed.password,
        FULLPATH=parsed.path,
        DATABASE=parsed.path.lstrip('/')
    )

    # Convert the dict to eliminate 'None' values
    sane_output = {
        k: (v or '')
        for k, v in output.items()
    }

    return sane_output
