from .. import catalogue_blueprint as bp


@bp.route("/zemi", methods=["GET"])
def get_catalogue():
    return "Catalogue API"
