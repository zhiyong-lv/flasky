from flask import render_template, redirect, request, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from .forms import LoginForm, RegistrationForm, UpdatePasswordForm, ResetPasswordForm, SubmitEmailForm
from ..models import User, TOKEN_KEY_CALL_BACK, TOKEN_KEY_USER_NAME, TOKEN_KEY_NEW_EMAIL
from .confirm_session import ConfirmSession, TASK_CONFIRM_RIGISTER, TASK_CHANGE_EMAIL


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm/handler/<token>', endpoint='confirm_handler', methods=['GET', 'POST'])
def confirm_email_handler(token):
    ConfirmSession.reloadSession(token)
    return redirect(url_for('main.index'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            session['name'] = user.username
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid User Name or Password')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        ConfirmSession(user, 'Confirm Your Account', 'auth/email/confirm',
                       **{TOKEN_KEY_CALL_BACK: TASK_CONFIRM_RIGISTER}).send_confirm_email()
        return redirect(url_for('main.index'))
    return render_template('auth/common.html', form=form, header='Register - Input Your Informations')


@auth.route('/update/password', endpoint='update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.org_password.data):
            User.query.filter_by(id=current_user.id).first().password = form.new_password.data
            db.session.commit()
            logout_user()
            return redirect(url_for('auth.login'))
    return render_template('auth/common.html', form=form, header='Update Password')


@auth.route('/reset/password', endpoint='try_reset_password', methods=['GET', 'POST'])
def try_reset_password():
    form = SubmitEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.email is not None:
            ConfirmSession(user, 'Reset Your Password', 'auth/email/reset').send_confirm_email()
            return redirect(url_for('main.index'))
        else:
            flash('Input user is invalide')
            return render_template('auth.login')
    return render_template('auth/common.html', form=form, header='Reset Password - Input Your Email')


@auth.route('/reset/password/<token>', endpoint='reset_password', methods=['GET', 'POST'])
def reset_password(token):
    try:
        username = User.get_values_from_token(token, TOKEN_KEY_USER_NAME).get(TOKEN_KEY_USER_NAME)
        user = User.query.filter_by(username=username).first()
        if not user.confirm(token):
            raise Exception
    except Exception as e:
        current_app.logger.error(e.message)
        flash('Your token is incorrect!')
        return redirect(url_for('auth.login'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.new_password.data
        db.session.commit()
        flash('Your password have been reset!')
        return redirect(url_for('auth.login'))
    return render_template('auth/common.html', form=form, header='Reset Password - Input Your New Password')


@auth.route('/reset/email', endpoint='reset_email', methods=['GET', 'POST'])
@login_required
def reset_email():
    form = SubmitEmailForm()
    if form.validate_on_submit():
        tokens = {TOKEN_KEY_CALL_BACK: TASK_CHANGE_EMAIL, TOKEN_KEY_NEW_EMAIL: form.email.data}
        ConfirmSession(current_user, 'Change Your Email', 'auth/email/confirm',
                       **tokens).send_confirm_email()
        return redirect(url_for('main.index'))
    return render_template('auth/common.html', form=form, header='Change Email - Input Your New Email')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
