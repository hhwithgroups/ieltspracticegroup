# -*- coding: utf-8 -*-

from flask import request, redirect, url_for, render_template, flash, current_app
from flask.ext.login import login_required, login_user, logout_user, current_user
from .. import app

class FlashMessage:
    INVITE_FAIL = 'Invite failed.\n%s have been deleted or you have invited him/her.'
    INVITE_SUCCESS = 'You invited %s to practice with you.\nWait for him/her accept the invitation.'
    ACCEPT_FAIL = 'Accept failed.\n%s have been deleted or invitation is invalid.'
    ACCEPT_SUCCESS = 'You accepted the invitation from %s.'
    DECLINED = 'You declined the invitation from %s.'
    DELETED = 'You deleted %s from your practice friends.'


def render_users(user_list, paginate=True, page=1):
    if paginate:
        pagination = user_list.paginate(
            page, per_page=current_app.config['SPEAKING_USERS_PER_PAGE'],
            error_out=False)
        users = pagination.items
    else:
        pagination = None
        users = user_list.all()
    recommends = []
    for u in users:
        availability = u.available_time
        common_time = u.available_time & current_user.available_time
        time_segs = [(availability >> i) & 1 for i in range(21)]
        common_time_segs = [(common_time >> i) & 1 for i in range(21)]
        recommends.append((u, time_segs, common_time_segs))
    return recommends, pagination


@app.route('/speaking')
@login_required
def speaking():
    return redirect(url_for('speaking_friends'))


@app.route('/speaking/recommendations')
@login_required
def speaking_recommends():
    max_invitation_cnt = app.config['SPEAKING_INVITATION_PER_DAY']
    users = current_user.recommended_users
    recommendations, _ = render_users(users, paginate=False)
    return render_template('speaking/recommendation.html',
                           type='recommendation',
                           users=recommendations,
                           today_invitation_cnt=max_invitation_cnt-current_user.today_invitation_cnt,
                           pagination=None)


@app.route('/speaking/invitation')
@login_required
def speaking_invitation():
    page = request.args.get('page', 1, type=int)
    users = current_user.inviting_users
    invited_users = current_user.invited_users.all()
    invitations, pagination = render_users(users, page=page)
    return render_template('speaking/invitation.html',
                           type='invitation',
                           users=invitations,
                           invited_users=invited_users,
                           pagination=pagination)


@app.route('/speaking/friends')
@login_required
def speaking_friends():
    page = request.args.get('page', 1, type=int)
    users = current_user.friends_users
    friends, pagination = render_users(users, page=page)
    return render_template('speaking/friends.html',
                           type='friends',
                           users=friends,
                           pagination=pagination)


@app.route('/speaking/invite/<id>')
@login_required
def speaking_invite(id):
    result = current_user.invite(id)
    if result:
        flash(FlashMessage.INVITE_SUCCESS % result[1].nickname)
    else:
        flash(FlashMessage.INVITE_FAIL % id)
    return redirect(url_for('speaking_recommends'))
    

@app.route('/speaking/accept/<id>')
@login_required
def speaking_accept(id):
    result = current_user.accept(id)
    if result:
        flash(FlashMessage.ACCEPT_SUCCESS % result[1].nickname)
    else:
        flash(FlashMessage.ACCEPT_FAIL % id)
    return redirect(url_for('speaking_invitation'))


@app.route('/speaking/decline/<id>')
@login_required
def speaking_decline(id):
    result = current_user.decline(id)
    if result:
        flash(FlashMessage.DECLINED % result[1].nickname)
    return redirect(url_for('speaking_invitation'))

    
@app.route('/speaking/delete/<id>')
@login_required
def speaking_delete(id):
    result = current_user.delete_friend(id)
    if result:
        flash(FlashMessage.DELETED % result[1].nickname)
    return redirect(url_for('speaking_friends'))

