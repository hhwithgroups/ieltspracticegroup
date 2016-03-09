# -*- coding: utf-8 -*-
__author__ = 'wei'

from flask import request, current_app
from flask.ext.login import UserMixin, AnonymousUserMixin
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from .. import db, app, login_manager
from .writing import Article, ArticleComment, ArticleAnnotation
from .admin import Permission, Role
from datetime import date
import hashlib


level = {1: 'IELTS 5',
         2: 'IELTS 6',
         3: 'IELTS 7',}


class Recommendation(db.Model):
    # recommending A to B
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    recommending_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recommend_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Invitation(db.Model):
    # a invitation sent from A to B
    __tablename__ = 'invitations'
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    accepted = db.Column(db.Boolean, default=False)
    invitation_date = db.Column(db.Date, default=date.today())


class Friend(db.Model):
    # user1 has a friend called user2
    __tablename__ = 'friends'
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class ActiveUser(db.Model):
    __tablename__ = 'active_users'
    id = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.Integer, default=0)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64))
    email = db.Column(db.String(64))
    qq = db.Column(db.String(32))
    qq_group = db.Column(db.String(32))
    level = db.Column(db.Integer)
    target_score = db.Column(db.Float, default=6)
    exam_passed = db.Column(db.Boolean, default=False)
    date_of_exam = db.Column(db.Date)
    available_time = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    password_hash = db.Column(db.String(128))
    avatar_hash = db.Column(db.String(32))
    last_recommended = db.Column(db.Date, default=date.min)
    profile_changed = db.Column(db.Boolean, default=False)
    last_invitation_date = db.Column(db.Date, default=date.min)
    today_invitation_cnt = db.Column(db.Integer, default=0)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # add wechat id
    openid1 = db.Column(db.String(40))
    wechat_id = db.Column(db.String(20))
    headimgurl = db.Column(db.String(150))
    modify_date = db.Column(db.Date, default=date.min)
    latest_login_date = db.Column(db.Date, default=date.min)

    # a invitation sent from A to B
    sent_invitations = db.relationship('Invitation',
                                foreign_keys=[Invitation.from_user_id],
                                backref=db.backref('from_user', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    recv_invitations = db.relationship('Invitation',
                                foreign_keys=[Invitation.to_user_id],
                                backref=db.backref('to_user', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    # recommending A to B
    recommandations = db.relationship('Recommendation',
                                foreign_keys=[Recommendation.recommend_to_id],
                                backref=db.backref('recommend_to', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    recommended_to = db.relationship('Recommendation',
                                foreign_keys=[Recommendation.recommending_id],
                                backref=db.backref('recommending',
                                                   lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    # user1 has a friend called user2
    friends = db.relationship('Friend',
                               foreign_keys=[Friend.user1_id],
                               backref=db.backref('user1', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    friends_to = db.relationship('Friend',
                                 foreign_keys=[Friend.user2_id],
                                 backref=db.backref('user2', lazy='joined'),
                                 lazy='dynamic',
                                 cascade='all, delete-orphan')

    comments = db.relationship('ArticleComment',
                               foreign_keys=[ArticleComment.author_id],
                               backref=db.backref('author', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    annotations = db.relationship('ArticleAnnotation',
                                   foreign_keys=[ArticleAnnotation.author_id],
                                   backref=db.backref('author', lazy='joined'),
                                   lazy='dynamic',
                                   cascade='all, delete-orphan')

    articles = db.relationship('Article',
                                foreign_keys=[Article.author_id],
                                backref=db.backref('author', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __init__(self, *args, **kargs):
        super(User, self).__init__(*args, **kargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = \
                hashlib.md5(self.email.encode('utf-8')).hexdigest()

        if self.role is None:
            self.role = Role.query.filter_by(name='User').first()

    @property
    def is_weixin_user(self):
        return True if self.openid1 else False

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def gravatar(self, size=100, default='monsterid', rating='g'):
        headimgurl = self.headimgurl
        # http://wx.qlogo.cn/mmopen/Ie7hL.../0
        # 用户头像，最后一个数值代表正方形头像大小（有0、46、64、96、132数值可选，
        # 0代表640*640正方形头像）
        if headimgurl:
            if headimgurl.endswith('/0'):
                headimgurl = headimgurl[:-2] + '/46'
            return headimgurl
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = (self.avatar_hash or
                hashlib.md5(self.email.encode('utf-8')).hexdigest())
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
                url=url, hash=hash, size=size, default=default, rating=rating)

    def generate_reset_password_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = password
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def _recommand(self):
        # --- Might be done entirely in DB ---
        # 0. remove recommended users
        # 1. get invited user, inviting user and friends IDs
        # 2. get users in the same level but not invited or friends
        # 3. get user IDs from result of step 2
        #    which have common available time
        # 4. get users randomly using IDs from step 3
        # 5. insert users into Recommendation table

        # step 0
        Recommendation.query.filter_by(recommend_to_id=self.id).delete()

        # step 1
        ids = User.query.with_entities(User.id) \
                        .join(Invitation, Invitation.to_user_id==User.id) \
                        .filter(Invitation.from_user_id==self.id) \
                        .all()
        invited_user_ids = [i[0] for i in ids]

        ids = User.query.with_entities(User.id) \
                        .join(Invitation, Invitation.from_user_id==User.id) \
                        .filter(Invitation.to_user_id==self.id) \
                        .all()
        inviting_user_ids = [i[0] for i in ids]

        ids = User.query.with_entities(User.id) \
                        .join(Friend, Friend.user2_id==User.id) \
                        .filter(Friend.user1_id==self.id) \
                        .all()
        friends_ids = [i[0] for i in ids]

        # step 2
        users = User.query.join(ActiveUser, ActiveUser.id==User.id) \
                          .filter(~User.id.in_(invited_user_ids),
                                  ~User.id.in_(inviting_user_ids),
                                  ~User.id.in_(friends_ids),
                                  User.id != self.id,
                                  User.level == self.level).all()

        # step 3
        common_time_ids = [u.id for u in users
                                if u.available_time & self.available_time != 0]

        # step 4
        rec_users = User.query.order_by(func.rand()) \
                              .filter(User.id.in_(common_time_ids)) \
                              .limit(app.config['SPEAKING_MAX_RECOMMEND'])

        # step 5
        for u in rec_users:
            r = Recommendation(recommend_to_id=self.id,
                               recommending_id=u.id)
            db.session.add(r)
        db.session.commit()


    @property
    def recommended_users(self):
        if self.last_recommended < date.today() or self.profile_changed:
            self._recommand()
            self.last_recommended = date.today()
            self.profile_changed = False
            db.session.add(self)
        users = User.query.join(Recommendation,
                                Recommendation.recommending_id==User.id) \
                          .filter(Recommendation.recommend_to_id==self.id)
        return users

    @property
    def inviting_users(self):
        users = User.query.join(Invitation, Invitation.from_user_id==User.id) \
                          .filter(Invitation.to_user_id==self.id)
        return users

    @property
    def invited_users(self):
        users = User.query.join(Invitation, Invitation.to_user_id==User.id) \
                          .filter(Invitation.from_user_id==self.id)
        return users

    @property
    def friends_users(self):
        users = User.query.join(Friend, Friend.user2_id==User.id) \
                          .filter(Friend.user1_id==self.id)
        return users

    @property
    def commented_articles(self):
        articles = Article.query.join(ArticleComment, \
                                      ArticleComment.article_id==Article.id) \
                                .filter(ArticleComment.author_id==self.id)
        return articles

    @property
    def annotated_articles(self):
        articles = Article.query.join(ArticleAnnotation, \
                                      ArticleAnnotation.article_id==Article.id) \
                                .filter(ArticleAnnotation.author_id==self.id)
        return articles

    @property
    def commented_and_annotated_articles(self):
        return self.commented_articles.union(self.annotated_articles)

#     @property
#     def today_invitation_cnt(self):
#         return Invitation.query.filter_by(from_user_id=self.id,
#                                           invitation_date=date.today()).count()

    def invite(self, id):
        if self.last_invitation_date != date.today():
            self.last_invitation_date = date.today()
            self.today_invitation_cnt = 0

        # 1. number of invitation not exceed
        if (self.today_invitation_cnt >=
            app.config['SPEAKING_INVITATION_PER_DAY']):
            return False

        # 1.5. number of friends not exceed
        if (self.friends_users.count() >=
            app.config['SPEAKING_MAX_FRIENDS']):
            return False

        # 2. invited user is valid
        user = User.query.filter_by(id=id).first()
        if user is None:
            return False

        # 3. invitation not exist
        invitation = Invitation.query.filter_by(from_user_id=self.id,
                                                to_user_id=user.id).first()
        if invitation is not None:
            return False

        # 4. they are not friends
        friend = Friend.query.filter_by(user1_id=self.id,
                                        user2_id=user.id).first()
        if friend is not None:
            return False

        # 5. add invitation
        invitation = Invitation(from_user_id=self.id,
                                to_user_id=user.id)
        db.session.add(invitation)

        self.today_invitation_cnt += 1

        # 6. remove recommendation
        recommendation = Recommendation.query \
                                       .filter_by(recommending_id=user.id,
                                                  recommend_to_id=self.id) \
                                       .first()
        if recommendation is not None:
            db.session.delete(recommendation)

        recommendation = Recommendation.query \
                                       .filter_by(recommending_id=self.id,
                                                  recommend_to_id=user.id) \
                                       .first()
        if recommendation is not None:
            db.session.delete(recommendation)

        return (True, user)

    def accept(self, id):
        # 1. inviting user is valid
        user = User.query.filter_by(id=id).first()
        if user is None:
            return False

        # 2. invitation is valid
        invitation = Invitation.query.filter_by(to_user_id=self.id,
                                from_user_id=user.id).first()
        if invitation is None:
            return False

        # 3. delete invitation
        db.session.delete(invitation)
        invitation = Invitation.query.filter_by(from_user_id=self.id,
                                to_user_id=user.id).first()
        if invitation is not None:
            db.session.delete(invitation)

        # 4. add friend
        f1 = Friend.query.filter_by(user1_id=user.id, user2_id=self.id).first()
        f2 = Friend.query.filter_by(user1_id=self.id, user2_id=user.id).first()
        if f1 is None and f2 is None:
            friend1 = Friend(user1_id=user.id, user2_id=self.id)
            friend2 = Friend(user1_id=self.id, user2_id=user.id)
            db.session.add(friend1)
            db.session.add(friend2)

        return (True, user)

    def decline(self, id):
        # 1. user is valid
        user = User.query.filter_by(id=id).first()
        if user is None:
            return False

        # 2. invitation is valid
        invitation = Invitation.query.filter_by(from_user_id=user.id,
                                to_user_id=self.id).first()
        if invitation is None:
            return False

        # 3. delete invitation
        db.session.delete(invitation)
        return (True, user)

    def delete_friend(self, id):
        # 1. user is valid
        user = User.query.filter_by(id=id).first()
        if user is None:
            return False

        # 2. friend is valid
        friend1 = Friend.query.filter_by(user2_id=self.id,
                                         user1_id=user.id).first()
        friend2 = Friend.query.filter_by(user1_id=self.id,
                                         user2_id=user.id).first()

        if friend1 is None or friend2 is None:
            result = False
        else:
            result = True

        # 3. delete friend
        if friend1 is not None:
            db.session.delete(friend1)
        if friend2 is not None:
            db.session.delete(friend2)

        return (result, user)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed, choice, randint
        import forgery_py

        seed()
        user_added = 0
        while user_added < count:
            u = User(email=forgery_py.internet.email_address(),
                     nickname=forgery_py.internet.user_name(),
                     password=forgery_py.lorem_ipsum.word(),
                     qq=forgery_py.basic.text(at_least=5,
                                              lowercase=False,
                                              uppercase=False,
                                              spaces=False),
                     qq_group=choice(app.config['SPEAKING_QQ_GROUPS']),
                     level=choice(level.keys()),
                     target_score=choice([i*0.5 for i in range(1, 19)]),
                     date_of_exam=forgery_py.date.date(),
                     exam_passed=choice((True, False)),
                     description=forgery_py.lorem_ipsum.paragraph(),
                     available_time=randint(1, 2**21-1))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
            else:
                user_added += 1

    '''
    def assign_admin(self): # disable this first
        admin_role = Role.query.filter_by(name='Administrator').first()
        self.role_id = admin_role.id
        db.session.add(self)
        db.session.commit()
    '''

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
