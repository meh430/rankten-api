from flask import Response, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import User
from errors import *
from database.json_cacher import *
import simdjson as json

# /users
# supports PUT
class UsersApi(Resource):
    # temp
    # get all users
    @schema_val_error
    def get(self):
        return Response(User.objects().to_json(), mimetype='application/json', status=200)

    # update user info
    @jwt_required
    @schema_val_error
    def put(self):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        body = request.get_json()
        if 'user_name' in body:
            body.pop('user_name')
        
        if 'rank_points' in body or 'date_created' in body or 'num_comments' in body or 'list_num' in body:
            raise SchemaValidationError

        if 'prof_pic' in body:
            user_comments = Comment.objects(user_name=user.user_name)
            for comment in user_comments:
                comment.update(prof_pic=body['prof_pic'])

        user.update(**body)
        return 'Updated user', 200

    # deletes user
    @jwt_required
    @schema_val_error
    def delete(self):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        user.delete()
        return 'Deleted user', 200
# /users/<name>
# supports GET
class UserApi(Resource):

    # get specific user info
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str):
        user = User.objects(user_name=name).exclude('password').first()
        user_json = json.loads(user.to_json())
        user_json['num_following'] = len(user.following)
        user_json['num_followers'] = len(user.followers)
        return user_json, 200
