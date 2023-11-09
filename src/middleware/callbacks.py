from flask import current_app, request, Response

from src import jwt

# from src import limiter
from .utils.process_error import failed_response

# from .utils.client import fetch_user_by_public_id_from_cache


# @limiter.request_filter
# def options_exclude():
#     """Exclude limiter on OPTIONS request."""
#     return request.method.upper() == "OPTIONS"


# @jwt.user_lookup_loader
# def user_lookup_callback(jwt_header: dict, jwt_payload: dict) -> dict:
#     """
#     A callback function that loads a user from the database (or cache) whenever
#     a protected route is accessed. This should return a dict containing the client info
#     on a successful lookup, or None if the lookup failed for any reason
#     (for example if the user cannot be found in the database).
#     This makes the client accessible at flask_jwt_extended.current_user
#     """
#     cache_conn = current_app.config["redis_users_cache_conn"]
#     return fetch_user_by_public_id_from_cache(jwt_payload["sub"], cache_conn)


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header: dict, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    entry = current_app.config["redis_login_connection"].get(jti)
    return True if entry is None else entry == "true"


@jwt.invalid_token_loader
def my_invalid_token_callback(invalid_token_loader: str) -> Response:
    return failed_response(401, "Invalid Token, Can't Complete Authorization")


@jwt.unauthorized_loader
def my_unauthorized_callback(unauthorized_loader: str) -> Response:
    return failed_response(401, "Missing Authorization Header")


@jwt.revoked_token_loader
def my_expired_token_callback(jwt_header: dict, jwt_payload: dict) -> Response:
    return failed_response(401, "Expired Token, Can't Complete Authorization")
