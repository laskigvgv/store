from .. import auth_blueprint as bp



@bp.route("/create", methods=["POST"])
def create_user():
    return "Create User API"
