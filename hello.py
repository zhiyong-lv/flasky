import os
from threading import Thread
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask import session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
from flask_mail import Mail, Message


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'data.sqllite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.live.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[LZY]'
app.config['FLASKY_MAIL_SENDER'] = os.environ.get('FLASKY_MAIL_SENDER') if (os.environ.get('FLASKY_MAIL_SENDER') is not None) else os.environ.get('MAIL_USERNAME')
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN') if (os.environ.get('FLASKY_ADMIN') is not None) else os.environ.get('MAIL_USERNAME')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
manager = Manager(app)
mail = Mail(app)


class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[Required()])
    submit = SubmitField("Submit")


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    login_name = session.get('name') if session.get('name') is not None else 'Stranger'
    session['name'] = login_name if form.name.data is None else form.name.data
    # first time, will return false, because client will send a GET request
    # instead of a POST request
    if form.validate_on_submit():
        existed_user = User.query.filter_by(username=form.name.data).first()
        if existed_user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User',
                           'mail/new_user', user=form.name.data)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = None
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(),
        form=form, known=session.get('known', False), name=session['name'])


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail_thread = Thread(target=send_async_email, args=(app, msg))
    mail_thread.start()
    return mail_thread


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, mail=mail)


manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
