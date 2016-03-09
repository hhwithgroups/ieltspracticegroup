# -*- coding: utf-8 -*-

from flask import request, redirect, url_for, render_template, flash
from flask.ext.login import login_required, login_user, logout_user,\
                            current_user
from .forms import RegisterForm, LoginForm, \
                   ResetPasswordRequestForm, ResetPasswordForm
from ..models import User, ActiveUser
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
        _update_latest_login_date(user)
        flash(FlashMessage.REGISTER_SUCCESS)
        return redirect(url_for('index'))
    return render_template('auth/register.html', form=form)

def _update_latest_login_date(user):
    db.engine.execute('update users set latest_login_date=now()'
            ' where id=%d' % user.id)
    active_user = ActiveUser.query.filter_by(id=user.id).first()
    if not active_user:
        active_user = ActiveUser(id=user.id)
        db.session.add(active_user)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            _update_latest_login_date(user)
            r = request.args.get('next') or url_for('index')
            if r == url_for('logout'):
                r = url_for('index')
            return redirect(r)
        flash(FlashMessage.LOGIN_FAILED)
    return render_template('auth/login.html', form=form)

@app.route('/weixin-login', methods=['GET', 'POST'])
def weixin_login():
    if hasattr(current_user, 'id'):
        _update_latest_login_date(current_user)
        return redirect('/speaking/friends')
    import urllib
    app_id = urllib.quote_plus(app.config['APP_ID'])
    r = ('https://open.weixin.qq.com/connect/oauth2/authorize?appid=' + app_id +
            '&redirect_uri=http%3A%2F%2Fieltspracticegroup.sinaapp.com%2Fweixin-auth-callback'
            '&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect')
    return redirect(r)

'''
https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxa7a1e9b980782576&redirect_uri=http%3A%2F%2Fieltspracticegroup.sinaapp.com%2Fweixin-auth-callback&response_type=code&scope=snsapi_userinfo&state=1#wechat_redirect
'''
@app.route('/weixin-auth-callback')
def weixin_auth_callback():
    import urllib, httplib, json
    code = urllib.quote_plus(request.args.get('code'))
    # /ielts/weixin_auth_callback.php?state=%2Fielts%2F&code=authdeny&reason=
    if not code or code == 'authdeny':
        #_HH: TODO: 用户拒绝微信登录 flash(FlashMessage.LOGIN_FAILED)
        return render_template('auth/login.html', form=LoginForm())
    app_id = urllib.quote_plus(app.config['APP_ID'])
    app_secret = urllib.quote_plus(app.config['APP_SECRET'])
    url = ('/sns/oauth2/access_token?'
           'appid=%s&secret=%s&code=%s&grant_type=authorization_code' %
           (app_id, app_secret, code))
    conn = httplib.HTTPSConnection('api.weixin.qq.com')
    conn.request('GET', url)
    response = conn.getresponse()
    access_token_response = json.loads(response.read())
    if access_token_response.has_key('errcode'):
        #_HH: TODO: 微信登录失败 flash(FlashMessage.LOGIN_FAILED)
        return render_template('auth/login.html', form=LoginForm())

    openid = access_token_response['openid']
    user = User.query.filter_by(openid1=openid).first()
    if user is not None:
        login_user(user, True)
        _update_latest_login_date(user)
        r = request.args.get('next') or '/speaking/friends'
        if r == url_for('logout'): r = '/speaking/friends'
        return redirect(r)

    access_token = access_token_response['access_token']
    url = ('/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN' %
           (urllib.quote_plus(access_token), urllib.quote_plus(openid)))
    conn = httplib.HTTPSConnection('api.weixin.qq.com')
    conn.request('GET', url)
    response = conn.getresponse()
    user_info_response = json.loads(response.read())
    if user_info_response.has_key('errcode'):
        #_HH: TODO: 微信获取用户信息失败 flash(FlashMessage.LOGIN_FAILED)
        return render_template('auth/login.html', form=LoginForm())

    nickname = user_info_response['nickname']
    headimgurl = user_info_response['headimgurl']
    user = User(email='', nickname=nickname, openid1=openid,
            headimgurl=headimgurl, available_time=0)
    db.session.add(user)
    db.session.commit()
    login_user(user, True)
    _update_latest_login_date(user)
    flash(FlashMessage.REGISTER_SUCCESS)
    return redirect('/profile')
    # return render_template('auth/weixin_auth_callback.html', access_token=access_token)

@app.route('/logout')
@login_required
def logout():
    if current_user.is_weixin_user :
         print 'logout ignored for weixin user'
         return redirect(url_for('index'))
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
