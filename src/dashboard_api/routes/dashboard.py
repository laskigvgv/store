from .. import dashboard_blueprint as bp


@bp.route("/admin", methods=["GET"])
def dashboard():
    return "Dashboard API"
