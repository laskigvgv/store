import os
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from werkzeug.utils import import_string

jwt = JWTManager()


load_dotenv()
CONFIG_TYPE = os.getenv("CONFIG_TYPE", default="config.DevConfig")
cfg = import_string(CONFIG_TYPE)()

bcrypt = Bcrypt()
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{cfg.REDIS_HOST}:6379/{cfg.CLIENT_RATE_LIMIT}",
    headers_enabled=True,
    key_prefix="store_api",
)


def create_app() -> Flask:
    """Function to instantiate the app."""

    # create a Flask app instance
    app = Flask("Store backend API")
    # # make the app recieve real client IP if it's behind one proxy
    # app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
    # apply app config
    app.config.from_object(cfg)
    # # add custom JSON provider class
    # app.json = CustomJsonProvider(app)

    # # initialize flask extensions
    initialize_extensions(app)
    # register middleware
    register_middleware(app)
    # register APIs
    register_apis(app)

    return app


def initialize_extensions(app: Flask) -> None:
    """Helper function to initialize app extensions."""
    bcrypt.init_app(app)
    jwt.init_app(app)
    # cache.init_app(app)
    limiter.init_app(app)


def register_apis(app: Flask) -> None:
    register_dashboard_api(app)
    register_catalogue_api(app)
    register_auth_api(app)


def register_dashboard_api(app: Flask) -> None:
    from src.dashboard_api import dashboard_blueprint

    url_prefix = "/dashboard"

    app.register_blueprint(dashboard_blueprint, url_prefix=url_prefix)


def register_catalogue_api(app: Flask) -> None:
    from src.catalogue_api import catalogue_blueprint

    url_prefix = "/catalogue"

    app.register_blueprint(catalogue_blueprint, url_prefix=url_prefix)


def register_auth_api(app: Flask) -> None:
    from src.auth_api import auth_blueprint

    url_prefix = "/auth"

    app.register_blueprint(auth_blueprint, url_prefix=url_prefix)


def register_middleware(app: Flask) -> None:
    from src.middleware import middleware_blueprint

    app.register_blueprint(middleware_blueprint)
