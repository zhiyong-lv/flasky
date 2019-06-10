from datetime import datetime
from flask import current_app, render_template, session, redirect, url_for
from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..email import send_email


@main.route('/', methods=['GET', 'POST'])
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
            app = current_app._get_current_object()
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User',
                           'mail/new_user', user=form.name.data)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = None
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(), form=form,
                           known=session.get('known', False), name=session['name'])
