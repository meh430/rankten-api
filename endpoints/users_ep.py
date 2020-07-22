from flask import Response, request
from database.user import User
from flask_restful import Resource


class Users(Resource):
    def get(self):
        return Response(User.objects().to_json(), mimetype='application/json', status=200)
