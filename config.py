import os
# import sae.const

class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_POOL_RECYCLE = 5 
    SPEAKING_USERS_PER_PAGE = 5
    SPEAKING_MAX_RECOMMEND = 5
    SPEAKING_INVITATION_PER_DAY = 3
    SPEAKING_MAX_FRIENDS = 10
    WRITING_ARTICLES_PER_PAGE = 3
    WRITING_COMMENTS_PER_PAGE = 5
    ADMIN_TOPICS_PER_PAGE = 5
    SSL = False
    SPEAKING_QQ_GROUPS = ['None',
                          'IELTS CLUB 1',
                          'IELTS CLUB 2',
                          'IELTS CLUB 3']
    SMTP_HOST = 'smtp.163.com'
    SMTP_PORT = 25,
    SMTP_USER = 'ieltsclubteam@163.com'
    SMTP_PASS = 'amkzuuojkukhwdva'
    APP_ID = 'wxa7a1e9b980782576'
    APP_SECRET = '79cbf1dba727d8538c95cea1c95cc89b'

class ProductConfig(Config):
    SECRET_KEY = 'O6T70gazj6kInjlRgj4DlWpSdmSy4jws'
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % \
                                ('ielts',
                                 'password',
                                 'localhost',
                                 '3306',
                                 'ieltspracticegroup',)
      
class DebugConfig(Config):
    DEBUG = True
    SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = 'mysql://yy:yyyyyyyy@127.0.0.1:3306/app_ieltspracticegroup'
    
    
class TestConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'secret'
    SQLALCHEMY_DATABASE_URI = 'mysql://yy:yyyyyyyy@127.0.0.1:3306/app_ieltspracticegroup'

