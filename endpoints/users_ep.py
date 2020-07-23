from flask import Response, request
from database.models import User
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity


class UsersApi(Resource):
    def get(self):
        return Response(User.objects().to_json(), mimetype='application/json', status=200)


class UserApi(Resource):

    # @jwt_required
    def get(self, id):
        return Response(User.objects.get(user_name=id).to_json(), mimetype='application/json', status=200)

    @jwt_required
    def put(self):
        uid = get_jwt_identity()
        user = User.objects.get(id=id)
        body = request.get_json()
        user.update(**body)
        return 'Updated user', 200
