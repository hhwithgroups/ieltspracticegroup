__author__ = 'wei'


from writing import Article, ArticleAnnotation, ArticleComment, WritingCategory, WritingTopic
from users import User, ActiveUser, Recommendation, Friend, Invitation, level
from admin import Role, Permission

from .. import login_manager
from .. import db


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_db():
    db.create_all()
    # a = WritingCategory.query.filter_by(category='--All--').first()
    # if a is None:
    #     a = WritingCategory(category='--All--', pseudo_all=True)
    #     db.session.add(a)
    #     db.session.commit()
    Role.insert_roles()
