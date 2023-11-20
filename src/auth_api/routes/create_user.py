from .. import auth_blueprint as bp
from flask import current_app, request, abort
from flask_bcrypt import Bcrypt
from src.utils.extras import validate_data, db_connection, read_query
from pydantic import BaseModel, Extra, StrictStr, validator, root_validator
import re
from ..sql import AUTH_API_QUERIES
from psycopg.errors import UniqueViolation


bcrypt = Bcrypt()

@bp.route("/create", methods=["PUT"])
def create_user():
    if not(body := request.get_json(silent=True)):
        abort(400, "Missing JSON in Request")

    pydantic_data = validate_data(body, ValidateRegisterInput)
    pydantic_data["password"] = bcrypt.generate_password_hash(pydantic_data["password"]).decode('utf-8')
    pydantic_data.pop('confirm_password')


    query = read_query(AUTH_API_QUERIES / "create_user.sql")

    db_pool = current_app.config['db_pool']
    try:
        with db_connection(db_pool) as conn:
            with conn.execute(query, pydantic_data) as cursor:
                result = cursor.fetchone()
    except UniqueViolation:
        abort(409, "Email already exists")

    return result

class ValidateRegisterInput(BaseModel, extra=Extra.forbid):

    email: StrictStr
    password: StrictStr
    confirm_password: StrictStr


    @validator("email")
    def check_email(cls, value):

        """
        Check regex if the string format is valid for an email.
        """

        regex = r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,7})+$"
        if not re.match(regex, value):
            raise ValueError("Not a valid Email.")
        return value

    @validator("password")
    def check_password_strength(cls, value):
        """
        Check if the password is over 8 characters long and if it
        contains lowercase/uppercase chars and a digit.
        """

        if len(value) <= 8:
            raise ValueError("The password needs to be longer than 8 characters")
        if not any(map(str.islower, value)):
            raise ValueError("The password should have at least one lowercase letter")
        if not any(map(str.isupper, value)):
            raise ValueError("The password should have at least one uppercase letter")
        if not any(map(str.isdigit, value)):
            raise ValueError("The password should have at least one digit")

        return value


    @root_validator
    def check_password_match(cls,values):
        """
        Check password missmatch
        """
        pw1 = values.get("password")
        pw2 =  values.get("confirm_password")
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("Passwords do not match")
        return values

