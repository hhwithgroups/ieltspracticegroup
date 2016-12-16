#!/usr/bin/env python

import os
import sys
absolute_path = os.path.abspath(__file__)
app_path = os.path.dirname(absolute_path)
path = os.path.join(app_path, 'libs')
sys.path.insert(0, path)
sys.path.insert(0, app_path)

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()
    
from app import app, db
from app.models import User, Invitation, Recommendation, Friend
from app.models import Article, ArticleComment, ArticleAnnotation, WritingCategory, WritingTopic
from app.models import Role, Permission
from flask.ext.script import Manager, Shell
# from flask.ext.migrate import Migrate, MigrateCommand

manager = Manager(app)
# migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db,
                User=User, Invitation=Invitation, Recommendation=Recommendation,
                Friend=Friend, Article=Article, ArticleAnnotation=ArticleAnnotation,
                ArticleComment=ArticleComment, WritingCategory=WritingCategory,
                WritingTopic=WritingTopic, Role=Role,
                Permission=Permission)

manager.add_command("shell", Shell(make_context=make_shell_context))
# manager.add_command("db", MigrateCommand)

@manager.command
def test(coverage=False):
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print 'Coverage Summary:'
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print 'HTML version: file://%s/index.html' % covdir
        COV.erase()
    
    
if __name__ == '__main__':
    manager.run()
