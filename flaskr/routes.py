from flask import redirect, url_for, session, request, jsonify, render_template
from flaskr import app, db
from flaskr.models import User, LeaveRequest, LeaveCategory
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
        return render_template('index.html', current_user=current_user)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    raw_data = json.dumps(google.get('userinfo').data)
    data = json.loads(raw_data)
    email = data['email']
    current_user = User.query.filter_by(email=email).first()
    if current_user.user_group == 'administrator':
        users = User.query.all()
        leave_categories = LeaveCategory.query.all()
        page = request.args.get('page', 1 , type=int)
        leave_requests = LeaveRequest.query.filter_by(state='pending').paginate(page, app.config.get('REQUESTS_PER_PAGE_ADMIN'), False)
        next_url = url_for('admin', page=leave_requests.next_num) \
        if leave_requests.has_next else None
        prev_url = url_for('admin', page=leave_requests.prev_num) \
        if leave_requests.has_prev else None
        return render_template('admin.html', users=users, leave_requests=leave_requests.items, next_url=next_url, prev_url=prev_url, leave_categories=leave_categories, user_groups=app.config.get('USER_GROUPS'))
    return redirect(url_for('index'))

@app.route('/requests')
def requests():
    raw_data = json.dumps(google.get('userinfo').data)
    data = json.loads(raw_data)
    email = data['email']
    current_user = User.query.filter_by(email=email).first()
    if current_user.user_group == 'administrator':
        page = request.args.get('page', 1 , type=int)
        leave_requests = LeaveRequest.query.order_by(LeaveRequest.start_date.asc()).paginate(page, app.config.get('REQUESTS_PER_PAGE'), False)
        next_url = url_for('requests', page=leave_requests.next_num) \
        if leave_requests.has_next else None
        prev_url = url_for('requests', page=leave_requests.prev_num) \
        if leave_requests.has_prev else None
        return render_template('requests.html', leave_requests=leave_requests.items, next_url=next_url, prev_url=prev_url)
    return redirect(url_for('index'))

@app.route('/account')
def account():
    raw_data = json.dumps(google.get('userinfo').data)
    data = json.loads(raw_data)
    email = data['email']
    current_user = User.query.filter_by(email=email).first()
    return render_template('account.html', current_user=current_user)

@app.route('/save_request', methods=["GET","POST"])
def save_request():
    current_user = User.query.filter_by(email=request.form.get('current_user')).first()
    if current_user.user_group == 'viewer' or current_user.user_group == 'unapproved':
        return redirect(url_for('index'))
    start_date_split = request.form.get('start-date').split("/")
    end_date_split = request.form.get('end-date').split("/")
    leave_request = LeaveRequest(start_date = datetime.datetime.strptime(start_date_split[2] + '-' + start_date_split[0] + '-' + start_date_split[1], '%Y-%m-%d'),
                                end_date = datetime.datetime.strptime(end_date_split[2] + '-' + end_date_split[0] + '-' + end_date_split[1], '%Y-%m-%d'),
                                state = 'pending',
                                user_id = current_user.id)
    if current_user.user_group == 'administrator':
        leave_request.state = 'accepted'
    db.session.add(leave_request)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/handle_request', methods=["POST"])
def handle_request():
    if request.method == 'POST':
        accept_request = request.form.get('accept')
        decline_request = request.form.get('decline')
        if accept_request is not None:
            leave_request = LeaveRequest.query.filter_by(id=accept_request).first()
            leave_request.state = 'accepted'
            db.session.commit()
        else:
            leave_request = LeaveRequest.query.filter_by(id=decline_request).first()
            leave_request.state = 'declined'
            db.session.commit()
    return redirect(url_for('admin'))

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
    max_days = request.form.get('max_days')
    if delete is not None:
        category = LeaveCategory.query.filter_by(id=delete).first()
        db.session.delete(user)
        db.session.commit()
    else:
        category = LeaveCategory(category = add, max_days = max_days)
        db.session.add(category)
        db.session.commit()
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

@app.template_filter('dateformat')
def dateformat(date):
    return date.strftime('%Y-%m-%d')
