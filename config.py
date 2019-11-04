import os
import logging


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_MAIL_SUBJECT_PREFIX = '[LZY]'
    FLASKY_MAIL_SENDER = os.environ.get('FLASKY_MAIL_SENDER') if (os.environ.get(
        'FLASKY_MAIL_SENDER') is not None) else os.environ.get('MAIL_USERNAME')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') if (os.environ.get(
        'FLASKY_ADMIN') is not None) else os.environ.get('MAIL_USERNAME')
    LOG_PATH = os.path.join(BASE_DIR, 'logs')
    LOG_PATH_INFO = os.path.join(LOG_PATH, 'info.log')
    LOG_FILE_MAX_BYTES = 100 * 1024 * 1024
    LOG_FILE_BACKUP_COUNT = 10
    FLASKY_POSTS_PER_PAGE = 20

    @classmethod
    def init_app(cls, app):
        app.config['SECRET_KEY'] = Config.SECRET_KEY
        app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = Config.SQLALCHEMY_COMMIT_ON_TEARDOWN
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
        app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = Config.FLASKY_MAIL_SUBJECT_PREFIX
        app.config['FLASKY_MAIL_SENDER'] = Config.FLASKY_MAIL_SENDER
        app.config['FLASKY_ADMIN'] = Config.FLASKY_ADMIN
        app.config['ENV'] = 'default'
        app.config['FLASKY_POSTS_PER_PAGE'] = Config.FLASKY_POSTS_PER_PAGE

        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename=cls.LOG_PATH_INFO,
                            filemode='w')
        app.logger = logging.getLogger()


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.live.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'data-dev.sqlite')
    ENV = 'DEV'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.config['SQLALCHEMY_DATABASE_URI'] = DevelopmentConfig.SQLALCHEMY_DATABASE_URI
        app.config['MAIL_SERVER'] = DevelopmentConfig.MAIL_SERVER
        app.config['MAIL_PORT'] = DevelopmentConfig.MAIL_PORT
        app.config['MAIL_USE_TLS'] = DevelopmentConfig.MAIL_USE_TLS
        app.config['MAIL_USERNAME'] = DevelopmentConfig.MAIL_USERNAME
        app.config['MAIL_PASSWORD'] = DevelopmentConfig.MAIL_PASSWORD
        app.config['ENV'] = cls.ENV


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    MAIL_SERVER = 'smtp.live.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'data-test.sqlite')
    ENV = 'TEST'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        app.config['SQLALCHEMY_DATABASE_URI'] = TestingConfig.SQLALCHEMY_DATABASE_URI
        app.config['MAIL_SERVER'] = TestingConfig.MAIL_SERVER
        app.config['MAIL_PORT'] = TestingConfig.MAIL_PORT
        app.config['MAIL_USE_TLS'] = TestingConfig.MAIL_USE_TLS
        app.config['MAIL_USERNAME'] = TestingConfig.MAIL_USERNAME
        app.config['MAIL_PASSWORD'] = TestingConfig.MAIL_PASSWORD
        app.config['TESTING'] = TestingConfig.TESTING
        app.config['ENV'] = cls.ENV


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'data.sqllite')
    ENV = 'PRD'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}


if __name__ == '__main__':
    print(config.get('development').ENV)
    print(config.get('testing').ENV)
