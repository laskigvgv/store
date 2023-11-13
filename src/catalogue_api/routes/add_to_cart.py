import json
from flask import abort, request, current_app
from pydantic import BaseModel, Extra, StrictInt, StrictStr
from src.utils.extras import read_query, validate_data, mongo_connection, db_connection
from ..sql import CATALOGUE_API_QUERIES
from .. import catalogue_blueprint as bp


@bp.route("/add", methods=["PUT"])
def add_to_cart():
    """
    Endpoint to add a product to the cart
    :method: PUT
    :input: JSON payload
        {
            "id": "product id",
            "quantity": "product quantity"
        }
    :return: JSON response
        {
            "status": "success",
            "message": "Product added successfully"
        }
    """

    # client_id = 2 hardcoded needs to be taken from the token when implemented
    client_id = 2

    # check for JSON body
    if not (body := request.get_json(silent=True)):
        abort(400, "Missing JSON Body in the Request")

    validated_data = validate_data(body, AddToCartModel)

    data = {"client_id": client_id}

    query = read_query(CATALOGUE_API_QUERIES / "get_cart.sql")

    # check if the user has already a cart in postgres database
    db_pool = current_app.config["db_pool"]
    with db_connection(db_pool) as conn:
        with conn.execute(query, data) as cursor:
            result = cursor.fetchall()

        # if the user has a cart, update it
        if result:
            items = result[0]["items"]

            # check if the product already exists in the cart if yess add plus the quantity to the existing one
            # else add the product to the cart

            if any(item["id"] == validated_data["id"] for item in items):
                for item in items:
                    if item["id"] == validated_data["id"]:
                        item["quantity"] += validated_data["quantity"]
                        data["items"] = json.dumps(items)

                        query = read_query(CATALOGUE_API_QUERIES / "update_cart.sql")

                        with conn.execute(query, data) as cursor:
                            cursor.fetchall()
                        return {
                            "status": "success",
                            "message": "Product updated successfully",
                        }
            else:
                query = read_query(CATALOGUE_API_QUERIES / "update_cart.sql")
                items.append(validated_data)
                data["items"] = json.dumps(items)

                with conn.execute(query, data) as cursor:
                    cursor.fetchall()

                return {"status": "success", "message": "Product added successfully"}

        # else create a new cart
        else:
            items = []
            items.append(validated_data)
            data["items"] = json.dumps(items)

            query = read_query(CATALOGUE_API_QUERIES / "create_cart.sql")

            with conn.execute(query, data) as cursor:
                cursor.fetchall()
    return {"status": "success", "message": "Product added successfully"}


class AddToCartModel(BaseModel):
    id: StrictStr
    quantity: StrictInt

    class Config:
        extra = Extra.forbid
