from .. import auth_blueprint as bp
import json
from flask import abort, request, jsonify, current_app
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from pydantic import BaseModel, Extra, StrictStr, validator, root_validator
from psycopg.errors import UniqueViolation
from src.utils.extras import validate_data, db_connection, read_query
import re
from ..sql import AUTH_API_QUERIES

bcrypt = Bcrypt()


@bp.route("/login", methods=["GET"])
def login_user():
    if not(body := request.get_json(silent=True)):
        abort(404, "Missing JSON in request")

    pydantic_data = validate_data(body, ValidateLoginInput)
    query = read_query(AUTH_API_QUERIES / "login_user.sql")
    db_pool = current_app.config["db_pool"]

    with db_connection(db_pool) as conn:
        with conn.execute(query, pydantic_data) as cursor:
            result = cursor.fetchone()
            if not result:
                abort(404, "User does not exist")
            if not bcrypt.check_password_hash(result["password"], pydantic_data["password"]):
                abort(401, "Wrong login info")
            # """
            # Get access and refresh tokens
            # """
            # access_token = create_access_token(identity=result["email"])
            # refresh_token = create_refresh_token(identity=result["email"])
            # """
            # get_jti encoded tokens
            # """
            # access_jti = get_jti(encoded_token=access_token)
            # refresh_jti  = get_jti(encoded_token=refresh_token)
            # print(access_jti, refresh_jti)

    response = {"message" : "Login successful"}


    return jsonify(response)





class ValidateLoginInput(BaseModel, extra=Extra.forbid):
    email: StrictStr
    password: StrictStr

    @validator("email")
    def check_email(cls, value):
        """
        Check regex if the string format is valid for an email.
        """
        regex = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,7})+$"
        if not re.match(regex, value):
            raise ValueError("Not a valid Email.")
        return value

