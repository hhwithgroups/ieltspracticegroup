# -*- coding: utf-8 -*-

from flask import request, redirect, url_for, render_template, flash
from flask.ext.login import login_required, login_user, logout_user,\
                            current_user
from .forms import RegisterForm, LoginForm, \
                   ResetPasswordRequestForm, ResetPasswordForm
from ..models import User
from .. import app, db
from ..email import send_email

class FlashMessage:
    REGISTER_SUCCESS = 'New user registered successfully.'
    LOGIN_FAILED = 'Invalid username or password.'
    LOGGED_OUT = 'You have been logged out, bye.'
    UNKNOWN_EMAIL = 'Unknown email address.'
    PASSWORD_RESET_FAIL = 'Reset password failed.'
    PASSWORD_RESET_SENT = 'A email has sent to you to reset your password.'
    PASSWORD_CHANGED = 'You have changed your password.'
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    nickname=form.nickname.data,
                    password=form.password.data,
                    qq=form.qq.data,
                    qq_group=form.qq_group.data,
                    level=form.level.data,
                    target_score=form.target_score.data,
                    date_of_exam=form.date_of_exam.data,
                    exam_passed=form.exam_passed.data,
                    description=form.description.data,
                    available_time=form.available_times)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(FlashMessage.REGISTER_SUCCESS)
        return redirect(url_for('index'))
    return render_template('auth/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            r = request.args.get('next') or url_for('index')
            if r == url_for('logout'):
                r = url_for('index')
            return redirect(r)
        flash(FlashMessage.LOGIN_FAILED)
    return render_template('auth/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(FlashMessage.LOGGED_OUT)
    return redirect(url_for('index'))


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password_req():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data).first()
        if u is None:
            flash(FlashMessage.UNKNOWN_EMAIL)
            return redirect(url_for('login'))
        token = u.generate_reset_password_token()
        send_email(u.email,
                   'IELTS Practice Group: Reset password',
                   '/mail/reset-password',
                   user=u,
                   token=token)
        flash(FlashMessage.PASSWORD_RESET_SENT)
        return redirect(url_for('login'))
    return render_template('/auth/reset-password-request.html', form=form)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data).first()
        if u is None:
            flash(FlashMessage.UNKNOWN_EMAIL)
            return redirect(url_for('login'))
        if u.reset_password(token, form.new_password.data):
            flash(FlashMessage.PASSWORD_CHANGED)
            return redirect(url_for('login'))
        else:
            flash(FlashMessage.PASSWORD_RESET_FAIL)
            return redirect(url_for('login')) 
    return render_template('/auth/reset-password.html', form=form)
