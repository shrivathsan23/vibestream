from datetime import datetime as dt

from vibestream import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)
    videos = db.relationship('Video', backref = 'uploader', lazy = True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(150), nullable = False)
    filename = db.Column(db.String(100), unique = True, nullable = False)
    upload_date = db.Column(db.DateTime, default = dt.utcnow)
    watch_count = db.Column(db.Integer, default = 0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __repr__(self):
        return f"Video('{self.title}', '{self.upload_date}')"