# from .. import auth_blueprint as bp
# import json
# from flask import abort, request, jsonify, current_app
# from flask_bcrypt import Bcrypt
# from flask_jwt_extended import create_access_token, create_refresh_token, get_jti
#
# bcrypt = Bcrypt()
#
# @bp.route("/login", methods=["PUT"])
# def login_user():
#     dummy_data = {'email': 'fzdravkoski@gmail.com',
#                   'password' : 'whatever'}
#     # request.get_json(silent=True)
#     if not (body := dummy_data):
#         abort(400, 'Missing json in request')
#
#     # Pydantic check to be made
#
#     hashed_password = "$2b$12$pPbW4s6qhM03hlWtVU1Fz.ltY.tRMvAlIJ05hYeCCmMv7AfwKBP.C"
#     print(hashed_password)
#     if bcrypt.check_password_hash(hashed_password, dummy_data['password'].encode('utf-8')):
#         access_token = create_access_token(identity=dummy_data['email'])
#         refresh_token = create_refresh_token(identity=dummy_data['email'])
#
#         access_jti = get_jti(encoded_token=access_token)
#         refresh_jti = get_jti(encoded_token=refresh_token)
#
#         token_data = {
#             "access_token" : access_token,
#             "refresh_token" : refresh_token
#         }
#     else:
#         abort(409, 'Invalid credentials')
#
#
#     return jsonify(token_data), 200
#
