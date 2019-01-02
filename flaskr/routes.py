from flask import redirect, url_for, session, request, jsonify, render_template
from flaskr import app, db
from flaskr.models import User, LeaveRequest
from flask_oauthlib.client import OAuth
import re, datetime, calendar
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
        raw_data = json.dumps(google.get('userinfo').data)
        data = json.loads(raw_data)
        email = data['email']
        current_user = User.query.filter_by(email=email).first()
        generate_calendar = calendar.HTMLCalendar(firstweekday=0)
        today = datetime.datetime.date(datetime.datetime.now())
        current = re.split('-', str(today))
        current_yr = int(current[0])
        return render_template('index.html', calendar_html=generate_calendar.formatyear(current_yr, 4), current_user=current_user)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    raw_data = json.dumps(google.get('userinfo').data)
    data = json.loads(raw_data)
    email = data['email']
    current_user = User.query.filter_by(email=email).first()
    if current_user.user_group == 'administrator':
        users = User.query.all()
        return render_template('admin.html', users=users, leave_categories=app.config.get('LEAVE_CATEGORIES'), user_groups=app.config.get('USER_GROUPS'))
    return redirect(url_for('index'))

@app.route('/handle_acc', methods=["GET","POST"])
def handle_acc():
    if request.method == 'POST':
        delete_email = request.form.get('delete')
        approve_email = request.form.get('approve')
        group = request.form.get('group')
        user_email = request.form.get('user')
        if delete_email is not None:
            user = User.query.filter_by(email=delete_email).first()
            db.session.delete(user)
            db.session.commit()
        elif approve_email is not None:
            user = User.query.filter_by(email=approve_email).first()
            user.user_group = 'viewer'
            db.session.commit()
        else:
            user = User.query.filter_by(email=user_email).first()
            user.user_group = group
            db.session.commit()
    return redirect(url_for('admin'))

@app.route('/handle_cat', methods=["POST"])
def handle_cat():
    delete = request.form.get('delete')
    add = request.form.get('add')
    categories = app.config.get('LEAVE_CATEGORIES')
    if delete is not None:
        categories.remove(delete)
        app.config.update(LEAVE_CATEGORIES=categories)
    else:
        if add:
            categories.append(add)
            app.config.update(LEAVE_CATEGORIES=categories)
    return redirect(url_for('admin'))

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
    email = data['email']
    existing = User.query.filter_by(email=email).first()
    if existing is None:
        user = User(email = email)
        db.session.add(user)
        db.session.commit()
    return redirect(url_for('index'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')
