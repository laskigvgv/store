from .. import catalogue_blueprint as bp


@bp.route("/", methods=["GET"])
def get_catalogue():
    return "Catalogue API"
