from flask import Flask


def create_app() -> Flask:
    """Function to instantiate the app."""

    # create a Flask app instance
    app = Flask("Store backend API")
    # # make the app recieve real client IP if it's behind one proxy
    # app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
    # # apply app config
    # app.config.from_object(cfg)
    # # add custom JSON provider class
    # app.json = CustomJsonProvider(app)
    # # add additional app config (redis and db pool objects)
    # update_app_config(app)
    # # initialize flask extensions
    # initialize_extensions(app)
    # register middleware
    # register_middleware(app)
    # register APIs
    register_apis(app)

    return app


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
