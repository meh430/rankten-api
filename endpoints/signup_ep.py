from flask import Response, request
from database.user import User
from database.list_collection import ListCollection
from flask_restful import Resource


class SignUp(Resource):
    def post(self):
        body = request.get_json()
        user_lists = ListCollection(user_name=body['user_name']).save()
        user = User(**body, created_lists=user_lists.id).save()
        return {'id': str(user.id)}, 200
