from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import User
from errors import *


class UsersApi(Resource):
    # get all users
    @internal_server_error
    @schema_val_error
    def get(self):
        return Response(User.objects().to_json(), mimetype='application/json', status=200)

    # update user info
    @schema_val_error
    @internal_server_error
    @jwt_required
    def put(self):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        body = request.get_json()
        user.update(**body)
        return 'Updated user', 200


class UserApi(Resource):

    # get specific user info
    @internal_server_error
    @schema_val_error
    @user_does_not_exist_error
    def get(self, name):
        return Response(User.objects.get(user_name=name).to_json(), mimetype='application/json', status=200)
