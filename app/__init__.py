from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()


def create_app(app_config):
    app = Flask(__name__)
    app_config.init_app(app)

    # initial app
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    mail.init_app(app)

    # Start to import blueprint
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')
    return app
