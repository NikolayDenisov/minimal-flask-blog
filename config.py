#!/usr/bin/env python3


class Config:
    # General
    FLASK_DEBUG = True
    SECRET_KEY = 'SECRET_KEY'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////opt/blog/blog.db'
    REMEMBER_COOKIE_DURATION = 60 * 60 * 24  # 24 hours
    DEBUG=True
