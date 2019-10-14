import unittest
from app.models import User, Role, Permission, AnonymousUser
from app import db, create_app
from config import config
from flask import current_app


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config.get('testing'))
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_roles_and_permissions(self):
        Role.insert_roles()
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()
        u.can(Permission.FOLLOW)

    def test_generate_confirmation_tokens(self):
        user = User(id=100)
        original_dict = {'username': 'test_user_name', 'email': 'test_email'}
        keys = original_dict.keys()
        token = user.generate_confirmation_token(**original_dict)
        current_app.logger.info(User.get_values_from_token(token, *keys))
        current_app.logger.info('current env is {}.'.format(current_app.config['ENV']))

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('cat1'))

    def test_password_salts_are_random(self):
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertFalse(u1.password_hash == u2.password_hash)

    def test_generate_confirmation_token(self):
        u1 = User(id=1, username='test')
        token = u1.generate_confirmation_token()
        self.assertTrue(u1.confirm(token))
