from shapely import wkb


def wkt_to_location(wkt_obj):
    """Converts a Well-Known Text element
    (WKTElement) to a location with parameters
    x and y.
    """
    return wkb.loads(bytes(wkt_obj.data))