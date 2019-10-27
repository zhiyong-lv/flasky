from flask import flash, current_app
from .. import db
from ..models import TOKEN_KEY_NEW_EMAIL
import hashlib


CALL_BACK_URL = 'auth.confirm_handler'


def confirm(token_json, user):
    flash('You have confirmed your account. Thanks!')


def change_email(token_json, user):
    new_email = token_json.get(TOKEN_KEY_NEW_EMAIL)
    if new_email is not None:
        user.email = new_email
        user.avatar_hash = hashlib.md5(user.email.encode('utf-8')).hexdigest()
        db.session.commit()
        flash('Your email have been changed!')
    else:
        current_app.logger.error("input token_json is {}".format(token_json))
        flash('Your email have not been changed! Please contact Admins')
