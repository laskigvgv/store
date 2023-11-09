import json
from werkzeug.exceptions import HTTPException

from . import middleware_blueprint as bp
from .utils.process_error import failed_response, process_error


@bp.app_errorhandler(404)
def page_not_found(e):
    return failed_response(404, e.description)


@bp.app_errorhandler(405)
def method_not_allowed(e):
    return failed_response(405, e.description)


@bp.app_errorhandler(429)
def ratelimit_handler(e):
    return failed_response(429, e.description)


@bp.app_errorhandler(500)
@bp.app_errorhandler(502)
@bp.app_errorhandler(503)
def internal_server_error(e):
    return process_error(e)


@bp.app_errorhandler(HTTPException)
def default_exception_handler(e):
    """
    Returns rich JSON response for every Flask known error.
    If error is 500+ process and notify.
    """
    if e.code > 500:
        return process_error(e)

    # form response
    response = failed_response(e.code, e.description)
    # get response data
    data = json.loads(response.data)
    # if error has generic title (from get_error_object)
    if data["title"] == f"Error {e.code}":
        # give proper title
        data["title"] = e.name
    # load back data to response
    response.data = json.dumps(data)

    return response
