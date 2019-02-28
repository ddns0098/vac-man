"""Flaskr module"""
import os
import os.path

from flask import Flask
from flask_mail import Mail


# create and configure the app
def create_app():
    """Creates and configures app."""
    app = Flask(__name__, instance_relative_config=True)

    try:
        app.config.from_pyfile('config.py')
    except IOError:
        print('Error: No config file. Use environment variables...')
        app.config.update(
            SECRET_KEY=os.getenv('SECRET_KEY'),
            GOOGLE_ID=os.getenv('GOOGLE_ID'),
            GOOGLE_SECRET=os.getenv('GOOGLE_SECRET'),
            USER_GROUPS=['viewer', 'employee', 'administrator'],
            SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI'))

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.app_context():
        from flaskr.models import db
        db.init_app(app)
        db.create_all()
        # pylint: disable=unused-variable
        mail = Mail(app)

        from flaskr.routes import routes_blueprint
        app.register_blueprint(routes_blueprint)

    return app
