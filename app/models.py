#!/usr/bin/python3

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Posts(db.Model):
    __tablename__ = 'posts'
    PER_PAGE = 5
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=1)
    tags = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<Post {}>'.format(self.body)
