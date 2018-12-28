from flaskr import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_group = db.Column(db.String(20), nullable=False)
    days = db.Column(db.Integer, default=20, nullable=False)
    leave_requests = db.relationship('LeaveRequest', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.email}', '{self.user_group}', '{self.days}')"

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    note = db.Column(db.Text, nullable=True)
    state = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"LeaveRequest('{self.start_date}', '{self.end_date}', '{self.note}', '{self.state}')"
