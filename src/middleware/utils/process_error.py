import uuid
import time
import traceback
import datetime
from typing import Any
from flask import current_app, make_response, Response


error_titles: dict[int, str] = {
    204: "No Content",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    415: "Unsupported Media Type",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Servic1e unavailable",
    503: "Service unavailable",
}


def failed_response(code: int, detail: str, title: str | None = None) -> Response:
    """
    Return Flask failed response given the code, detail and optionally title.
    Add id, metadata, title, status, detail, headers and status code to response.

    :param: code: status code of the response.
    :param: detail: explanation of failure.
    :param: title: name of the error.
    """

    title = error_titles.get(code, f"Error {code}") if title is None else title
    body = {
        "id": str(uuid.uuid1()).replace("-", ""),
        "meta": {"timestamp": str(time.time()).replace(".", "")},
        "title": title,
        "status": code,
        "code": code,
        "detail": detail,
    }

    return make_response(body, code)


def process_error(e):
    """Gets original exception if any and sends notifications."""
    # prepare vars
    API_ENV = current_app.config["API_ENV"]
    error_status_code = e.code or 500
    error_message = "Server Error, Please Try Again Later"
    fail_resp = None
    error_string = "Suite API Fail, Check Error Log"
    traceback_verbose = None

    # try to get the original exception details
    try:
        exception = e.original_exception
        # if exception args in a dict
        if exception.args and isinstance(args := exception.args[0], dict):
            # get error details
            error_status_code = args.get("status_code") or error_status_code
            error_message = args.get("error_message") or error_message
            fail_resp = args.get("fail_resp") or fail_resp

            # form error string
            if original_err_str := args.get("error_string"):
                error_string = f"{error_string} \n {original_err_str}"

        # form traceback
        error_string += f" \n ENV: {API_ENV} \n TRACEBACK: {traceback.format_exc()}"
        tb = traceback.TracebackException.from_exception(exception, capture_locals=True)
        traceback_locals = tb.format()
        traceback_verbose = "".join(traceback_locals)

    # if there isn't original exception, pass
    except AttributeError:
        pass

    # return notifier
    return service_notifier(
        error_string,
        error_status_code,
        error_message,
        fail_resp,
        env=API_ENV,
        traceback_verbose=traceback_verbose,
    )


def service_notifier(
    error_string: str,
    error_status_code: int,
    error_message: str,
    fail_resp: Response | None = None,
    env: str = "dev",
    in_app_context: bool = True,
    error_notification_queue=None,
    traceback_verbose: str | None = None,
) -> Response | Any:
    """
    Prepares notification for notification queue as well as a failed response.
    Returns response to be returned to the user.
    """

    error_string = f"Timestamp: {datetime.datetime.now()} \n{error_string}"
    if env != "production":
        print(error_string, "=== EXCEPTION ===")

    def notify_for_this_code(status_code: int) -> bool:
        return status_code in [429, None] or status_code >= 500

    if fail_resp:
        if notify_for_this_code(fail_resp.status_code):
            notify(
                msg_body=error_string,
                error_notification_queue=error_notification_queue,
                traceback_verbose=traceback_verbose,
            )
        return fail_resp

    if notify_for_this_code(error_status_code):
        notify(
            msg_body=error_string,
            error_notification_queue=error_notification_queue,
            traceback_verbose=traceback_verbose,
        )

    if not in_app_context or error_status_code == None:
        return 1

    return failed_response(error_status_code, error_message)


def notify(
    msg_body: str = "",
    msg_subject: str = "Error on Server!",
    send_to=None,
    error_notification_queue=None,
    traceback_verbose=None,
) -> None:
    """
    Function that prepares body for error notification queue.
    Actually adds to redis queue.
    """

    mail_body = {
        "msg_body": msg_body,
        "msg_subject": msg_subject,
        "send_to": send_to,
        "traceback_verbose": traceback_verbose,
    }

    if not error_notification_queue:
        error_notification_queue = current_app.config["error_notification_queue"]

    error_notification_queue.add_to_task_queue(mail_body)
