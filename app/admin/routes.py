import logging

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user

import app
from app.admin.forms import LoginForm
from app.models import Users

blueprint = Blueprint(
    'admin_blueprint',
    __name__,
    url_prefix='',
    template_folder='templates')


@blueprint.route('/login', methods=['GET', 'POST'])
def route_login():
    if current_user.is_authenticated:
        return redirect(url_for('base_blueprint.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            logging.debug('Invalid username or password')
            flash('Invalid username or password')
            return redirect(url_for('admin_blueprint.route_login'))
        logging.debug('Success!')
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('base_blueprint.home'))
    return render_template('login.html', title='Sign In', form=form)


@app.login.user_loader
def load_user(id):
    return Users.query.get(int(id))


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.home'))
