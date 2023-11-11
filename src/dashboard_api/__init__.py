import os
from flask import Blueprint, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import import_string, find_modules
from src import limiter


dashboard_blueprint = Blueprint("dashboard", __name__)
CLIENT_RATE_LIMIT = os.getenv("CLIENT_RATE_LIMIT")


# apply security checks on all admin_api routes
# =================we should add admin protection here================
@dashboard_blueprint.before_request
@limiter.limit(f"{CLIENT_RATE_LIMIT} per minute")
def check_for_access_token():
    pass


# make all the routes modules directly importable
for module in find_modules("src.dashboard_api.routes"):
    import_string(module)
