from .. import dashboard_blueprint as bp

from flask import abort, request, current_app
from src.utils.extras import validate_data, mongo_connection
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
            "image_url": "product image url"
        }
    :return: JSON response
        {
            "status": "success",
            "message": "Product added successfully"
        }
    """
    # connection to MongoDB
    mongo_client = mongo_connection()
    collection = mongo_client.store.products

    print("imame konekcija do mongodb")
    # check for JSON body
    if not (body := request.get_json(silent=True)):
        abort(400, "Missing JSON Body in the Request")

    validated_data = validate_data(body, AddProductModel)

    # check if product already exists
    if collection.find_one({"name": validated_data["name"]}):
        abort(409, "Product already exists")

    # insert product to the database
    collection.insert_one(validated_data)

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
