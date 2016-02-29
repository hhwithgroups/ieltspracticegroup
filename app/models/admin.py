__author__ = 'wei'

from .. import db

class Permission:
    COMMENT = 0X01
    WRITE_ARTICLE = 0X02
    ADMINISTER = 0X04

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': Permission.COMMENT | Permission.WRITE_ARTICLE,
            'Administrator': 0xff
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r, permissions=roles[r])
            db.session.add(role)
        db.session.commit()
