from .. import auth_blueprint as bp
from flask import current_app, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
from src.utils.extra import validate_data, db_connection

methods = ['OPTIONS', 'POST']


bcrypt = Bcrypt()



@bp.route("/create", methods=["POST"])
def create_user():
    if not(body := request.get_json(silent=True)):
        abort(400, "Missing JSON in Request")

    data = validate_data(body, RegisterClient)
    flask_redis = current_app.config["redis_users_cache_conn"]
    print(flask_redis)
    if user_collections.find_one({'email' : user_email}):
        return jsonify({'message': 'User already exists!'})

    hashed_pass = bcrypt.generate_password_hash(user_password).decode('utf-8')

    user_data = {
        'email' : user_email,
        'password' : hashed_pass
    }

    user_collections.insert_one(user_data)

    access_token = create_access_token(identity=user_email)
    refresh_token = create_refresh_token(identity=user_email)

    access_jti = get_jti(encoded_token=access_token)
    refresh_jti = get_jti(encoded_token=refresh_token)

    current_app.flask_redis.set(access_jti, "false", 86400)
    current_app.flask_redis.set(refresh_jti, "false", 86400)

    tokens = {
        "access_token" : access_token,
        "refresh_token" : refresh_token
    }


    return jsonify(tokens), 200
