from flask import redirect, url_for, session, request, jsonify, render_template, flash
from flaskr import app, db, mail
from flaskr.models import User, LeaveRequest, LeaveCategory
from .decorators import asynchronous
from flask_oauthlib.client import OAuth
from flask_mail import Message
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
        current_user = get_current_user()
        return render_template('index.html', current_user=current_user)
    return redirect(url_for('login'))

@app.route('/admin')
def admin():
    current_user = get_current_user()
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
    current_user = get_current_user()
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
    current_user = get_current_user()
    if current_user.leave_category is None:
        days_left = "You don't have a leave category yet."
    else:
        days_left = get_days_left(current_user)
    return render_template('account.html', current_user=current_user, days_left=days_left)

@app.route('/save_request', methods=["GET","POST"])
def save_request():
    current_user = User.query.filter_by(email=request.form.get('current_user')).first()
    if current_user.user_group == 'viewer' or current_user.user_group == 'unapproved':
        return redirect(url_for('index'))
    start_date_split = request.form.get('start-date').split("/")
    end_date_split = request.form.get('end-date').split("/")
    start_date = datetime.datetime.strptime(start_date_split[2] + '-' + start_date_split[0] + '-' + start_date_split[1], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date_split[2] + '-' + end_date_split[0] + '-' + end_date_split[1], '%Y-%m-%d')
    days = end_date - start_date
    if days.days + 1 <= get_days_left(current_user):
        leave_request = LeaveRequest(start_date = start_date,
                                    end_date = end_date,
                                    state = 'pending',
                                    user_id = current_user.id)
        if current_user.user_group == 'administrator':
            leave_request.state = 'accepted'
        current_user.days += days.days + 1
        db.session.add(leave_request)
        db.session.commit()
        change = current_user.email + " created a leave request."
        send_email(change)
        return redirect(url_for('index'))
    flash("You only have " + str(get_days_left(current_user)) + " days left!")
    return redirect(url_for('index'))

@app.route('/handle_request', methods=["POST"])
def handle_request():
    if request.method == 'POST':
        accept_request = request.form.get('accept')
        decline_request = request.form.get('decline')
        if accept_request is not None:
            leave_request = LeaveRequest.query.filter_by(id=accept_request).first()
            if leave_request.state != 'pending':
                days = leave_request.end_date - leave_request.start_date
                leave_request.user.days += days.days + 1
            leave_request.state = 'accepted'
            db.session.commit()
            change = leave_request.user.email + "'s leave request has been accepted."
            send_email(change, leave_request.user.email)
        else:
            leave_request = LeaveRequest.query.filter_by(id=decline_request).first()
            leave_request.state = 'declined'
            days_back = leave_request.end_date - leave_request.start_date
            leave_request.user.days -= days_back.days + 1
            db.session.commit()
            change = leave_request.user.email + "'s leave request has been declined."
            send_email(change, leave_request.user.email)
        if request.form.get('site'):
            return redirect(url_for('requests'))
    return redirect(url_for('admin'))

@app.route('/handle_acc', methods=["GET","POST"])
def handle_acc():
    if request.method == 'POST':
        delete_email = request.form.get('delete')
        approve_email = request.form.get('approve')
        group = request.form.get('group')
        category = request.form.get('category')
        user_email = request.form.get('user')
        on = request.form.get('on')
        off = request.form.get('off')
        if on or off is not None:
            if on is not None:
                user = User.query.filter_by(email=on).first()
                user.notification = False
                db.session.commit()
            else:
                user = User.query.filter_by(email=off).first()
                user.notification = True
                db.session.commit()
            return redirect(url_for('account'))

        if delete_email is not None:
            user = User.query.filter_by(email=delete_email).first()
            db.session.delete(user)
            db.session.commit()
            change = user_email + "'s account has been deleted."
            send_email(change, user_email)
        elif approve_email is not None:
            user = User.query.filter_by(email=approve_email).first()
            user.user_group = 'viewer'
            db.session.commit()
            change = user.email + " has been approved."
            send_email(change, user.email)
        elif category is not None:
            user = User.query.filter_by(email=user_email).first()
            user.leave_category_id = category
            db.session.commit()
            change = user.email + "'s category has been changed."
            send_email(change, user.email)
        else:
            user = User.query.filter_by(email=user_email).first()
            user.user_group = group
            db.session.commit()
            change = user.email + "'s user group has been changed."
            send_email(change, user.email)
    return redirect(url_for('admin'))

@app.route('/handle_cat', methods=["POST"])
def handle_cat():
    delete = request.form.get('delete')
    add = request.form.get('add')
    max_days = request.form.get('max_days')
    if delete is not None:
        category = LeaveCategory.query.filter_by(id=delete).first()
        db.session.delete(category)
        db.session.commit()
        change = category.category + " leave category has been deleted."
        send_email(change)
    else:
        category = LeaveCategory(category = add, max_days = max_days)
        db.session.add(category)
        db.session.commit()
        change = category.category + " leave category has been added."
        send_email(change)
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
        change = user.email + " logged in for the first time."
        send_email(change)
    return redirect(url_for('index'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.template_filter('dateformat')
def dateformat(date):
    return date.strftime('%Y-%m-%d')

def get_current_user():
    raw_data = json.dumps(google.get('userinfo').data)
    data = json.loads(raw_data)
    email = data['email']
    return User.query.filter_by(email=email).first()

def get_days_left(user):
    return user.leave_category.max_days - user.days

@asynchronous
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(change, email=None):
    admins = User.query.filter_by(user_group='administrator', notification=True).all()
    emails = []
    for admin in admins:
        emails.append(admin.email)
    if email is not None:
        user = User.query.filter_by(email=email).first()
        if user.user_group != 'administrator' and user.notification:
            emails.append(user.email)
    msg = Message('Vacation Management',
                sender='noreply@demo.com',
                recipients=emails)
    msg.body = f'''There has been a change:
{change}

If you would like to turn off the notifications then turn it off in your account settings.
'''
    send_async_email(app, msg)
