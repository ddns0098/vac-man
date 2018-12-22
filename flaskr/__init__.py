import os

from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth

REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    oauth = OAuth()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    google = oauth.remote_app('google',
    base_url='https://www.googleapis.com/oauth2/v1/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    request_token_params={'scope': 'email'},
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'))

    @app.route('/')
    def index():
        if 'google_token' in session:
            me = google.get('userinfo')
            #Check data
            #return jsonify({"data": me.data})
            return render_template('index.html')
        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        return google.authorize(callback=url_for('authorized', _external=True))

    @app.route('/logout')
    def logout():
        session.pop('google_token', None)
        return redirect(url_for('index'))

    @app.route('/login/authorized')
    def authorized():
        resp = google.authorized_response()
        if resp is None:
            return 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
                )
        session['google_token'] = (resp['access_token'], '')
        me = google.get('userinfo')
        return jsonify({"data": me.data})

    @google.tokengetter
    def get_google_oauth_token():
        return session.get('google_token')

    from . import db
    db.init_app(app)

    return app
