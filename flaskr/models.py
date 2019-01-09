from flaskr import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_group = db.Column(db.String(20), default='unapproved', nullable=False)
    days = db.Column(db.Integer, default=0, nullable=False)
    notification = db.Column(db.Boolean, default=True, nullable=False)
    leave_requests = db.relationship('LeaveRequest', backref='user', lazy=True)
    leave_category_id = db.Column(db.Integer, db.ForeignKey('leave_category.id'), nullable=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.user_group}', '{self.days}', '{self.notification}')"

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"LeaveRequest('{self.start_date}', '{self.end_date}', '{self.state}')"

class LeaveCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(120), unique=True, nullable=False)
    max_days = db.Column(db.Integer, default=20, nullable=False)
    users = db.relationship('User', backref='leave_category', lazy=True)

    def __repr__(self):
        return f"LeaveCategory('{self.category}', '{self.max_days}')"
