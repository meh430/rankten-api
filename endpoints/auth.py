from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from database.models import *
from errors import *
import datetime


class SignUpApi(Resource):
    # create new user document and return generated jwt token
    @user_already_exists_error
    @schema_val_error
    @internal_server_error
    def post(self):
        body = request.get_json()
        user_lists = ListCollection()
        user_lists.save()
        user = User(**body, created_lists=user_lists)
        user.hash_pass()
        user.save()
        user_lists.update(belongs_to=user)
        acc_token = create_access_token(identity=str(
            user.id), expires_delta=datetime.timedelta(minutes=25.0))
        return {'jwt_token': acc_token}, 200


class LoginApi(Resource):
    # return newly generated jwt token for login
    @user_does_not_exist_error
    @schema_val_error
    @internal_server_error
    def post(self):
        body = request.get_json()
        user = User.objects.get(user_name=body['user_name'])
        auth = user.check_password(body['password'])
        if not auth:
            raise UnauthorizedError

        acc_token = create_access_token(identity=str(
            user.id), expires_delta=datetime.timedelta(minutes=25.0))
        return {'jwt_token': acc_token}, 200
