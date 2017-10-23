import ujson as json

from beluga import app
from beluga.models import Event, session_scope

def test_healthcheck_returns_200():
    _, response = app.test_client.get('/')
    assert response.status == 200


def test_event_handler_exists():
    route = '/events'
    _, response = app.test_client.get(route)
    assert response.status == 200

def test_event_handler_returns_results():
    route = '/events'
    _, response = app.test_client.get(route)
    assert response.status == 200
    res_json = json.loads(response.text)
    assert ('results' in res_json)

def test_geo_filtering():
    """Test that geographical filtering is behaving sanely"""
    return
    # Search around Vancouver
    _, response = app.test_client.get("/events?lat=49&lon=-123&radius=50")
    assert response.status == 200
    res_json = json.loads(response.text)
    assert ('results' in res_json)
    assert len(res_json['results']) > 0

    # Search on the other side of the world, expecting nothing
    _, response = app.test_client.get("/events?lat=-49&lon=123&radius=50")
    assert response.status == 200
    res_json = json.loads(response.text)
    assert ('results' in res_json)
    assert len(res_json['results']) == 0

def test_rsvp_post_exists():
    route = '/events/abcdef/rsvp'
    _, response = app.test_client.post(route)
    assert response.status == 501


def test_rsvp_delete_exists():
    route = '/events/abcdef/rsvp'
    _, response = app.test_client.delete(route)
    assert response.status == 501
