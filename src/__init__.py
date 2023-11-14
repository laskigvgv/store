import os
import redis
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from psycopg.conninfo import make_conninfo
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from dotenv import load_dotenv
from werkzeug.utils import import_string

from .database.database_config_pool import DatabasePool

from .utils.redis_queue import RedisQueue

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
    # add additional app config (redis and db pool objects)
    update_app_config(app)
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


def update_app_config(app: Flask) -> None:
    """Helper function to add objects to app config."""

    ### Create database poll ###
    ############################

    with app.app_context():
        db_conn_pool = DatabasePool(
            min_conn=app.config["DB_POOL_MIN_CONN"],
            max_conn=app.config["DB_POOL_MAX_CONN"],
        )

    ### Create redis connections ###
    ################################

    redis_login_connection = redis.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=app.config["LOGIN_DB_CONN"],
        decode_responses=True,
    )

    redis_users_cache_conn = redis.Redis(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        db=app.config["CLIENT_CACHE_DB"],
        decode_responses=True,
    )

    ### Create redis queues ###
    ###########################

    error_notification_queue = RedisQueue(
        host=app.config["REDIS_HOST"],
        port=app.config["REDIS_PORT"],
        queue_name="notification_queue",
        queue_db=13,
    )

    # db_insertion_queue = None
    # if "main_api" in app.config.get("APIS_IN_USE", []):
    #     db_insertion_queue = RedisQueue(
    #         queue_name="db_insertion_queue",
    #         queue_db=14,
    #         host=app.config["REDIS_HOST"],
    #         port=app.config["REDIS_PORT"],
    #     )

    # Place all objects that we created in app.config.
    # These are in app.config (which is a dict) because of typing reasons.
    # If they were added as app instance attributes the typing linter will not
    # recognize them as valid because they would have been dynamically added.
    ############################################################################

    app.config.update(
        {
            "db_pool": initialize_db_pool(app),
            "db_conn_pool": db_conn_pool,
            "redis_login_connection": redis_login_connection,
            "redis_users_cache_conn": redis_users_cache_conn,
            "error_notification_queue": error_notification_queue,
            # "db_insertion_queue": db_insertion_queue,
        }
    )


def initialize_db_pool(app: Flask) -> ConnectionPool:
    """
    Create an instance of a threaded psycopg3 pool.
    https://www.psycopg.org/psycopg3/docs/api/pool.html#psycopg_pool.ConnectionPool
    """

    # prepare connection string
    # https://www.psycopg.org/psycopg3/docs/api/conninfo.html
    conninfo = make_conninfo(
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        host=app.config["DB_HOST"],
        port=5432,
        dbname=app.config["DB_NAME"],
    )

    # return psycopg3 database pool instance
    return ConnectionPool(
        conninfo=conninfo,
        min_size=app.config.get("DB_POOL_MIN_CONN", 1),
        max_size=app.config.get("DB_POOL_MAX_CONN", 2),
        kwargs={"row_factory": dict_row},
    )
