from .. import dashboard_blueprint as bp

from flask import abort, request
from src.utils.extras import validate_data
from pydantic import BaseModel, Extra, StrictStr, StrictInt, HttpUrl


@bp.route("/add", methods=["PUT"])
def add_product():
    """
    Endpoint to add a product to the catalogue
    :method: PUT
    :input: JSON payload
        {
            "category: "product category",
            "name": "product name",
            "price": "product price",
            "quantity": "product quantity"
            "description": "product description"
            "imge_url": "product image url"
        }
    :return: JSON response
        {
            "status": "success",
            "message": "Product added successfully"
        }
    """

    # check for JSON body
    if not (body := request.get_json(silent=True)):
        abort(400, "Missing JSON Body in the Request")

    validated_data = validate_data(body, AddProductModel)

    return {"status": "success", "message": "Product added successfully"}


class AddProductModel(BaseModel):
    category: StrictStr
    name: StrictStr
    price: StrictInt
    quantity: StrictInt
    description: StrictStr
    image_url: HttpUrl

    class Config:
        extra = Extra.forbid
