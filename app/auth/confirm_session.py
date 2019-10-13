from .service import CALL_BACK_URL, confirm, change_email
from ..models import User, TOKEN_KEY_USER_NAME, TOKEN_KEY_CURRENT_EMAIL, TOKEN_KEY_CALL_BACK, TOKEN_KEYS
from ..email import send_email
from flask import flash, redirect, url_for, current_app


TASK_CONFIRM_RIGISTER = 'confirm_reg'
TASK_CHANGE_EMAIL = 'change_email'
TASKS_MAP = {
    TASK_CONFIRM_RIGISTER: confirm,
    TASK_CHANGE_EMAIL: change_email
}


class ConfirmSession:
    def __init__(self, user, subject, template, **kwargs):
        self._user = user
        self._subject = subject
        self._template = template
        self._token_json = {
            TOKEN_KEY_USER_NAME: self._user.username,
            TOKEN_KEY_CURRENT_EMAIL: self._user.email
            }
        self._token_json.update(kwargs)

    @staticmethod
    def reloadSession(token):
        try:
            token_json = User.get_values_from_token(
                token, *TOKEN_KEYS)
            username = token_json.get(TOKEN_KEY_USER_NAME)
            task_key = token_json.get(TOKEN_KEY_CALL_BACK)
            current_app.logger.info("task_key is {}.".format(task_key))
            do_task = TASKS_MAP.get(task_key)
            user = User.query.filter_by(username=username).first()
            if user is None or not user.confirm(token):
                current_app.logger.error("user {} unconfirm".format(username))
                raise Exception
            do_task(token_json, user)
        except Exception as e:
            current_app.logger.error("reason is {}. token_json is {}".format(e, token_json))
            flash('The confirmation link is invalid or has expired.')

    def send_confirm_email(self):
        send_email(self._get_email(), self._subject, self._template, url=CALL_BACK_URL,
                   user=self._user, token=self._get_token())
        flash('A confirmation email has been sent to you by email')
        return redirect(url_for('main.index'))

    def _get_token(self):
        return self._user.generate_confirmation_token(**(self._token_json))

    def _get_token_json(self):
        return self._token_json

    def _get_email(self):
        return self._user.email
