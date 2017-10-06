from beluga import app


def test_healthcheck_returns_200():
    request, response = app.test_client.get('/')
    assert response.status == 200


def test_event_handler_exists():
    route = '/events'
    request, response = app.test_client.get(route)
    assert response.status == 501


def test_rsvp_post_exists():
    route = '/events/abcdef/rsvp'
    request, response = app.test_client.post(route)
    assert response.status == 501


def test_rsvp_delete_exists():
    route = '/events/abcdef/rsvp'
    request, response = app.test_client.delete(route)
    assert response.status == 501
