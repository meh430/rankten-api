from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from database.models import *
from errors import *
import datetime

# /signup
# supports POST


class SignUpApi(Resource):
    """
    schema:
    {
        "user_name": string,
        "password": string,
        "bio": optional string
    }
    """
    # creates a new user document and return generated jwt token
    @user_already_exists_error
    @schema_val_error
    def post(self):
        body = request.get_json()
        user_lists = ListCollection()
        user_lists.save()
        user = User(**body, created_lists=user_lists)
        user.hash_pass()
        user.save()
        user_lists.update(belongs_to=user)
        acc_token = create_access_token(identity=str(
            user.id), expires_delta=datetime.timedelta(days=7))
        return {'jwt_token': acc_token}, 200

# /login
# supports POST


class LoginApi(Resource):
    # return newly generated jwt token for login
    """
    schema:
    {
        "user_name": string,
        "password": string
    }
    """
    @user_does_not_exist_error
    @schema_val_error
    def post(self):
        body = request.get_json()
        user = User.objects.get(user_name=body['user_name'])
        auth = user.check_password(body['password'])
        if not auth:
            raise UnauthorizedError

        acc_token = create_access_token(identity=str(
            user.id), expires_delta=datetime.timedelta(minutes=55.0))
        return {'jwt_token': acc_token}, 200

# /validate_token
# supports POST


class TokenApi(Resource):
    # checks token validity
    @jwt_required
    def post(self):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        return {'user_name': str(user.user_name)}, 200
