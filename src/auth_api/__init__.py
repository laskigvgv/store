from flask import Blueprint
from flask_jwt_extended import jwt_required
from werkzeug.utils import import_string, find_modules


auth_blueprint = Blueprint("auth", __name__)


# apply security checks on all admin_api routes
@auth_blueprint.before_request
def check_for_access_token():
    pass


# make all the routes modules directly importable
for module in find_modules("src.auth_api.routes"):
    import_string(module)
