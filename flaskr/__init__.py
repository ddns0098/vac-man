import os

from flask import Flask
from flask_mail import Mail

# create and configure the app
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config.from_pyfile('config.py')
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')

    with app.app_context():
        from flaskr.models import db
        db.init_app(app)
        db.create_all()
        mail = Mail(app)

        from flaskr.routes import routes_blueprint
        app.register_blueprint(routes_blueprint)

    return app
