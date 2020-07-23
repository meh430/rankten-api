from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import User


class UsersApi(Resource):
    # get all users
    def get(self):
        return Response(User.objects().to_json(), mimetype='application/json', status=200)

    # update user info
    @jwt_required
    def put(self):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        body = request.get_json()
        user.update(**body)
        return 'Updated user', 200


class UserApi(Resource):

    # get specific user info
    def get(self, name):
        return Response(User.objects.get(user_name=name).to_json(), mimetype='application/json', status=200)
