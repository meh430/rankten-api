from flask import Response, request
from database.user import User
from flask_restful import Resource


class UsersApi(Resource):
    def get(self):
        return Response(User.objects().to_json(), mimetype='application/json', status=200)


class UserApi(Resource):
    def get(self, id):
        return Response(User.objects.get(id=id).to_json(), mimetype='application/json', status=200)
