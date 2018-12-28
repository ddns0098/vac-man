from flask import redirect, url_for, session, request, jsonify, render_template
from flaskr import app, db
from flaskr.models import User, LeaveRequest
from flask_oauthlib.client import OAuth
import json

REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console

oauth = OAuth()

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
    raw_data = json.dumps(google.get('userinfo').data)
    data = json.loads(raw_data)
    user = User(email = data['email'])
    existing = User.query.filter_by(email=user.email).first()
    if existing is None:
        db.session.add(user)
        db.session.commit()
    return redirect(url_for('index'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')
