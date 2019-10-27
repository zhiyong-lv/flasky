import unittest
from app.models import User, TOKEN_KEY_CALL_BACK
from app.auth.confirm_session import ConfirmSession, TASKS_MAP, TASK_CONFIRM_RIGISTER
from app import db, create_app
from config import config
from flask import current_app


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config.get('testing'))
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_email(self):
        original_dict = {'id': 100, 'username': 'test_user_name', 'email': 'test_email'}
        # keys = original_dict.keys()
        user = User(**original_dict)
        confirm_session = ConfirmSession(user, None, None)
        assert (confirm_session._get_email() == 'test_email')
        # token = user.generate_confirmation_token(**original_dict)
        # current_app.logger.info(User.get_values_from_token(token, *keys))
        # current_app.logger.info('current env is {}.'.format(current_app.config['ENV']))

    def test_get_token(self):
        original_dict = {'id': 100, 'username': 'test_user_name',
                         'email': 'test_email'}
        user = User(**original_dict)
        db.session.add(user)
        confirm_session = ConfirmSession(
            user, None, None, **{TOKEN_KEY_CALL_BACK: TASK_CONFIRM_RIGISTER})
        current_app.logger.debug(
            "confirm session's token is {}".format(confirm_session._get_token()))

        # def do_task(token_json, user):
        #     assert(token_json == original_dict)
        #     assert(user.id == 100)
        #     pass
        # TASKS_MAP[TOKEN_KEY_CALL_BACK] = do_task
        ConfirmSession.reloadSession(confirm_session._get_token())
