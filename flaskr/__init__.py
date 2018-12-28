import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_DATABASE_URI='sqlite:///site.db',
)
db = SQLAlchemy(app)

from flaskr import routes

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass
