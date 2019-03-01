import flaskr
from unittest import mock


@mock.patch('flaskr.routes.get_current_user')
def test_admin_page(get_mock_user, app, client):
    mock_user = flaskr.models.User()
    mock_user.user_group = 'administrator'
    mock_user.email = 'mock.admin@gmail.com'

    get_mock_user.return_value = mock_user

    assert(get_mock_user().user_group == 'administrator')

    resp = client.get('/admin')
    assert resp.status_code == 200


@mock.patch('flaskr.routes.get_current_user')
def test_requests_page(get_mock_user, app, client):
    mock_user = flaskr.models.User()
    mock_user.user_group = 'administrator'
    mock_user.email = 'mock.admin@gmail.com'

    get_mock_user.return_value = mock_user

    assert(get_mock_user().user_group == 'administrator')

    resp = client.get('/requests')
    assert resp.status_code == 200


@mock.patch('flaskr.routes.get_current_user')
def test_account_page(get_mock_user, app, client):
    mock_user = flaskr.models.User()
    mock_user.user_group = 'employee'
    mock_user.email = 'mock.employee@gmail.com'

    get_mock_user.return_value = mock_user

    assert(get_mock_user().user_group == 'employee')

    resp = client.get('/account')
    assert resp.status_code == 200
