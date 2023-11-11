from .. import dashboard_blueprint as bp

from flask import abort, request, current_app
from src.utils.extras import validate_data, mongo_connection
from pydantic import BaseModel, Extra, StrictStr, StrictInt, HttpUrl


@bp.route("/remove", methods=["DELETE"])
def remove_product():
    """
    Endpoint to remove a product from the catalogue
    :method: DELETE
    :input: JSON payload
        {
            "name": "product name"
        }
    :return: JSON response
        {
            "status": "success",
            "message": "Product removed successfully"
        }
    """

    # connection to MongoDB
    mongo_client = mongo_connection()
    collection = mongo_client.store.products

    # check for JSON body
    if not (body := request.get_json(silent=True)):
        abort(400, "Missing JSON Body in the Request")

    validated_data = validate_data(body, RemoveProductModel)

    # check if product exists
    if not collection.find_one({"name": validated_data["name"]}):
        abort(404, "Product not found")

    # remove product from the database
    collection.delete_one({"name": validated_data["name"]})

    return {"status": "success", "message": "Product removed successfully"}


class RemoveProductModel(BaseModel):
    name: StrictStr

    class Config:
        extra = Extra.forbid
