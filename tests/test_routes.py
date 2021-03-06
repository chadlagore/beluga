import ujson as json

from beluga import app
from tests.utils import (
    mock_events,
    add_db_categories,
    new_db,
    mock_users,
    magic_bearer_token # Contains a token we can use to authenticate requests
)


def test_healthcheck_returns_200():
    _, response = app.test_client.get('/')
    assert response.status == 200


def test_event_handler_exists():
    route = '/events'
    _, response = app.test_client.get(route, headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 200

def test_event_handler_returns_results():
    route = '/events'
    _, response = app.test_client.get(route, headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 200
    res_json = json.loads(response.text)
    assert ('results' in res_json)


@mock_events()
def test_geo_filtering():
    """Test that geographical filtering is behaving sanely"""
    # Search around Vancouver
    _, response = app.test_client.get("/events?lat=49&lon=-123&radius=50", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 200
    res_json = json.loads(response.text)
    assert ('results' in res_json)
    assert len(res_json['results']) > 0

    # Search on the other side of the world, expecting nothing
    _, response = app.test_client.get("/events?lat=-49&lon=123&radius=50", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 200
    res_json = json.loads(response.text)
    assert ('results' in res_json)
    assert len(res_json['results']) == 0


def test_start_end_time_event_route():
    """Test that geographical filtering is behaving sanely"""
    _, response = app.test_client.get("/events?start_time=abc", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 400

    _, response = app.test_client.get("/events?end_time=abc", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 400

    _, response = app.test_client.get(
        "/events?end_time=2014/01/01&start_time=2014/01--02", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 400


def test_bad_limit():
    _, response = app.test_client.get("/events?limit=somanybig", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 400


def test_bad_lat_lon_rad():
    _, response = app.test_client.get("/events?lat=in&lon=", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 400


def test_good_lat_lon_rad():
    _, response = app.test_client.get("/events?lat=1&lon=2&rad=12", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 200


@mock_events()
def test_good_start_end():
    _, response = app.test_client.get(
        "/events?start_time=2014-01-01&end_time=2050-01-05", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 200
    assert len(response.json) > 0


@mock_events()
def test_good_limit():
    _, response = app.test_client.get("/events?limit=1", headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert response.status == 200
    assert len(response.json) == 1


@new_db()
@add_db_categories([{'category_id': 117, 'name': 'new_cat1'}])
def test_category_endpoint():
    route = '/categories'
    _, response = app.test_client.get(route, headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert len(response.json['results']) == 1
    assert response.json['results'][0] == 'new_cat1'


@new_db()
@mock_events()
def test_category_filter():
    route = '/events?category=new_cat1'
    _, response = app.test_client.get(route, headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert len(response.json['results']) == 1
    assert response.json['results'][0]['category'] == 'new_cat1'

    route = '/events?category=new_cat2'
    _, response = app.test_client.get(route, headers={
        'Authorization': 'Bearer GOOD_TEST_TOKEN'
    })
    assert len(response.json['results']) == 1
    assert response.json['results'][0]['category'] == 'new_cat2'

@new_db()
@mock_events()
@mock_users()
def test_create_rsvp():
    route = '/events/27489090610/rsvp'
    _, response = app.test_client.post(route, headers={
        'Authorization': 'Bearer {}'.format(magic_bearer_token)
    })
    assert response.status == 204

    # Do it again, it should be idempotent
    _, response = app.test_client.post(route, headers={
        'Authorization': 'Bearer {}'.format(magic_bearer_token)
    })
    assert response.status == 204

@new_db()
@mock_events()
@mock_users()
def test_delete_rsvp():
    route = '/events/27489090610/rsvp'
    _, response = app.test_client.delete(route, headers={
        'Authorization': 'Bearer {}'.format(magic_bearer_token)
    })
    assert response.status == 204

    # Do it again, it should be idempotent
    _, response = app.test_client.delete(route, headers={
        'Authorization': 'Bearer {}'.format(magic_bearer_token)
    })
    assert response.status == 204

@new_db()
@mock_events()
@mock_users()
def test_retreive_rsvp():
    # Create the RSVP
    route = '/events/27489090610/rsvp'
    _, response = app.test_client.delete(route, headers={
        'Authorization': 'Bearer {}'.format(magic_bearer_token)
    })
    assert response.status == 204

    _, response = app.test_client.get('/events', headers={
        'Authorization': 'Bearer {}'.format(magic_bearer_token)
    })
    assert response.status == 200

    for e in response.json['results']:
        if e['id'] == '27489090610':
            assert len(e['attendees']) == 1
        else:
            assert len(e['attendees']) == 0


