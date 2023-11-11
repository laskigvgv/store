from src.utils.extras import mongo_connection
from .. import catalogue_blueprint as bp


@bp.route("/get", methods=["GET"])
def get_catalogue():
    """
    Endpoint to get the catalogue
    :method: GET
    :input: None

    :return: JSON response
        {
            "catalogue": [
                {
                    "category": "product category",
                    "name": "product name",
                    "price": "product price",
                    "quantity": "product quantity"
                    "description": "product description"
                    "image_url": "product image url"
                }
            ]
        }
    """

    # connection to MongoDB
    mongo_client = mongo_connection()
    collection = mongo_client.store.products

    # get all products from the database
    products = collection.find({}, {"_id": 0})

    # return products
    return {
        "catalogue": list(products),
    }
