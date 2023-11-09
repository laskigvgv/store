from flask import Blueprint

middleware_blueprint = Blueprint("middleware", __name__)

# make the middleware modules directly importable
from . import callbacks, errors, process_request
