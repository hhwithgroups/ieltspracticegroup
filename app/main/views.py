# -*- coding: utf-8 -*-

from flask import request, redirect, url_for, render_template, flash
from flask.ext.login import login_required, login_user, logout_user, \
                            current_user, current_app, abort
from .forms import ProfileForm
from ..models import User
from .. import app, db

class FlashMessage:
    UPDATE_PROFILE_SUCCESS = 'You have updated you profile.'

@app.route('/')
@login_required
def index():
    return redirect(url_for('writing'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.qq = form.qq.data
        current_user.wechat_id = form.wechat_id.data
        current_user.level = form.level.data
        current_user.target_score = form.target_score.data
        current_user.date_of_exam = form.date_of_exam.data
        current_user.exam_passed = form.exam_passed.data
        current_user.description = form.description.data
        current_user.available_time = form.available_times
        current_user.profile_changed = True
        db.session.add(current_user)
        flash(FlashMessage.UPDATE_PROFILE_SUCCESS)
        return redirect(url_for('speaking'))
    form.qq.data = current_user.qq
    form.wechat_id.data = current_user.wechat_id
    form.level.data = current_user.level
    form.target_score.data = current_user.target_score
    form.date_of_exam.data = current_user.date_of_exam
    form.exam_passed.data = current_user.exam_passed
    form.description.data = current_user.description
    form.available_times = current_user.available_time
    return render_template('profile.html', form=form)


@app.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
