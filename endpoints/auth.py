from flask import Response, request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from database.models import User, ListCollection
import datetime


class SignUpApi(Resource):
    # create new user document and return generated jwt token
    def post(self):
        body = request.get_json()
        user_lists = ListCollection(user_name=body['user_name'])
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
    def post(self):
        body = request.get_json()
        user = User.objects.get(user_name=body['user_name'])
        auth = user.check_password(body['password'])
        if not auth:
            return {'error': 'invalid credentials'}, 401

        acc_token = create_access_token(identity=str(
            user.id), expires_delta=datetime.timedelta(minutes=25.0))
        return {'jwt_token': acc_token}, 200
