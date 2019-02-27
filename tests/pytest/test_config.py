import os
def test_development_config(app):
    app.config.from_object('instance.config')
    assert not app.config['TESTING']
    assert app.config['GOOGLE_ID']
    assert app.config['GOOGLE_SECRET']
    assert app.config['SECRET_KEY']
    assert app.config['REQUESTS_PER_PAGE_ADMIN']
    assert app.config['REQUESTS_PER_PAGE']
    assert app.config['USER_GROUPS'] == ['viewer', 'employee', 'administrator']
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///site.db'
