import ujson as json

from beluga import app
from tests.utils import (
    mock_events,
    add_db_categories,
    new_db
)


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


@mock_events()
def test_geo_filtering():
    """Test that geographical filtering is behaving sanely"""
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


def test_start_end_time_event_route():
    """Test that geographical filtering is behaving sanely"""
    _, response = app.test_client.get("/events?start_time=abc")
    assert response.status == 400

    _, response = app.test_client.get("/events?end_time=abc")
    assert response.status == 400

    _, response = app.test_client.get(
        "/events?end_time=2014/01/01&start_time=2014/01--02")
    assert response.status == 400


def test_bad_limit():
    _, response = app.test_client.get("/events?limit=somanybig")
    assert response.status == 400


def test_bad_lat_lon_rad():
    _, response = app.test_client.get("/events?lat=in&lon=")
    assert response.status == 400


def test_good_lat_lon_rad():
    _, response = app.test_client.get("/events?lat=1&lon=2&rad=12")
    assert response.status == 200


@mock_events()
def test_good_start_end():
    _, response = app.test_client.get(
        "/events?start_time=2014-01-01&end_time=2050-01-05")
    assert response.status == 200
    assert len(response.json) > 0


@mock_events()
def test_good_limit():
    _, response = app.test_client.get("/events?limit=1")
    assert response.status == 200
    assert len(response.json) == 1


def test_rsvp_post_exists():
    route = '/events/abcdef/rsvp'
    _, response = app.test_client.post(route)
    assert response.status == 501


def test_rsvp_delete_exists():
    route = '/events/abcdef/rsvp'
    _, response = app.test_client.delete(route)
    assert response.status == 501


@new_db()
@add_db_categories([{'category_id': 117, 'name': 'new_cat1'}])
def test_category_endpoint():
    route = '/categories'
    _, response = app.test_client.get(route)
    assert len(response.json['results']) == 1
    assert response.json['results'][0] == 'new_cat1'
