__author__ = 'wei'

from .. import db
from datetime import datetime


class ArticleComment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))


class ArticleAnnotation(db.Model):
    __tablename__ = 'annotations'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    # topic = db.Column(db.String(1024))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    category_id = db.Column(db.Integer, db.ForeignKey('writing_categories.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('writing_topics.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('ArticleComment',
                               foreign_keys=[ArticleComment.article_id],
                               backref=db.backref('article', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    annotations = db.relationship('ArticleAnnotation',
                                  foreign_keys=[ArticleAnnotation.article_id],
                                  backref=db.backref('article', lazy='joined'),
                                  lazy='dynamic',
                                  cascade='all, delete-orphan')

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def annotation_count(self):
        return self.annotations.count()


def next_issue_number():
    last_issue_number = WritingTopic.query \
                                    .with_entities(WritingTopic.issue_number) \
                                    .order_by(WritingTopic.issue_number.desc()).first()
    if not last_issue_number:
        return 1
    else:
        return last_issue_number[0] + 1


class WritingTopic(db.Model):
    __tablename__ = 'writing_topics'

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.Text)
    issue_number = db.Column(db.Integer, default=next_issue_number, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    deleted = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('writing_categories.id'))
    articles = db.relationship('Article',
                               foreign_keys=[Article.topic_id],
                               backref=db.backref('topic', lazy="joined"),
                               lazy='dynamic',
                               cascade='all, delete-orphan')


class WritingCategory(db.Model):
    __tablename__ = 'writing_categories'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(128), unique=True)
    # pseudo_all = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)
    articles = db.relationship('Article',
                               foreign_keys=[Article.category_id],
                               backref=db.backref('category', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    topics = db.relationship('WritingTopic',
                             foreign_keys=[WritingTopic.category_id],
                             backref=db.backref('category', lazy='joined'),
                             lazy='dynamic',
                             cascade='all, delete-orphan')

    @staticmethod
    def insert_categories():
        categories = ['Technology', 'Education', 'Government',
                      'Society', 'Employment', 'Environment',
                      'Parents / Children', 'Gender Issue']
        for c in categories:
            c = WritingCategory(category=c)
            db.session.add(c)
        a = WritingCategory(category='--All--', pseudo_all=True)
        db.session.add(a)
        db.session.commit()
