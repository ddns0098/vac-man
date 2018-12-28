import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///site.db',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)
db = SQLAlchemy(app)

from flaskr import routes

# load the instance config, if it exists, when not testing
app.config.from_pyfile('config.py', silent=True)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

from . import db
db.init_app(app)
