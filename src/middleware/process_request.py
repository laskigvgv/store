import functools
from flask import request, make_response, current_app, Response
from . import middleware_blueprint as bp


@functools.cache
def get_allowed_methods(rule: str) -> set:
    """
    Fetches allowed methods for a given application rule
    by iterating through all the registered internal rules for the
    current app that match the given rule and extracts their methods.

    This is needed because there are endpoints with identical rules
    but different allowed methods.

    This function is cached with `@functools.cache` so the rule's methods
    are held into memory once the rule is called once.

    Args:
        rule (str): Practically an URI, i.e. "/v1/onboarding".

    Returns:
        set: A set of allowed methods for the given rule.
    """

    app_rules = current_app.url_map.iter_rules()
    rules = [r for r in app_rules if r.rule == rule]
    return {m for r in rules if r.methods for m in r.methods}


@bp.before_app_request
def preprocess_request() -> Response | None:
    """On OPTIONS request return standardized response."""

    # If no url_rule in request it's a request with unallowed method.
    # Let the specific route handle the request.
    if (rule := request.url_rule) is None:
        return

    # If this is not an OPTIONS request,
    # also let the specific route handle the request
    if request.method != "OPTIONS":
        return

    # Rule must be string because functools needs hashable argument
    allowed_methods = get_allowed_methods(str(rule))
    allowed_headers = "Authorization"

    if {"POST", "PUT"} & allowed_methods:
        allowed_headers += ", Content-Type"
    allowed_methods = ", ".join(allowed_methods)

    response = make_response({"success": True}, 200)
    response.headers["Access-Control-Allow-Headers"] = allowed_headers
    response.headers["Access-Control-Allow-Methods"] = allowed_methods
    return response


@bp.after_app_request
def postprocess_request(response: Response) -> Response:
    """Add headers on response made by any endpoint."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Server"] = "dade-holding.com"
    return response
