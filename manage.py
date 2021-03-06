import os

from flask import Flask
from flask_migrate import MigrateCommand
from flask_script import Manager, Shell

from app import create_app, db
from app.models import Role, User, Post, Comment
from config import config


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Comment=Comment)


if __name__ == '__main__':
    app = Flask(__name__)
    app = create_app(config.get(os.getenv('FLASK_CONFIG') or 'default'))
    manager = Manager(app)
    manager.add_command("shell", Shell(make_context=make_shell_context))
    manager.add_command('db', MigrateCommand)

    @manager.command
    def test():
        """Run the unit tests"""
        import unittest
        import coverage
        cov = coverage.Coverage(source=['./app', 'manaage.py'])
        cov.start()
        app.logger.info('current env is {}.'.format(app.config['ENV']))
        tests = unittest.TestLoader().discover('tests')
        unittest.TextTestRunner(verbosity=2).run(tests)
        app.logger.info('current env is {}.'.format(app.config['ENV']))
        cov.stop()
        cov.save()

        cov.html_report()

    manager.run()
