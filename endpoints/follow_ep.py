from flask import jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from errors import *
from database.models import User
from database.db import cache
from endpoints.users_ep import get_compact_uinfo
import json

# /follow/<name>
# supports POST


class FollowApi(Resource):
    # follows/unfollows specified user
    @jwt_required
    @user_does_not_exist_error
    @schema_val_error
    def post(self, name: str):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        if user.user_name == name:
            raise FollowError
        target = User.objects.get(user_name=name)
        exec_follow = target not in user.following

        if exec_follow:
            user.update(push__following=target,
                        inc__following_num=1)
            target.update(push__followers=user,
                          inc__followers_num=1)
        else:
            user.update(pull__following=target,
                        dec__following_num=1)
            target.update(pull__followers=user,
                          dec__followers_num=1)

        cache.delete(user.user_name + 'following')
        cache.delete(target.user_name + 'followers')

        return ('followed user' if exec_follow else 'unfollowed user'), 200

# /following/<name>
# supports GET


class FollowingApi(Resource):
    # returns a list of user's followed by the specified user
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str):
        if cache.exists(name + 'following'):
            return cache.get(name + 'following'), 200
        else:
            following_json = json.dumps(get_compact_uinfo(
                User.objects.get(user_name=name).following))
            cache.set(name + 'following', following_json)

            return following_json, 200

# /followers/<name>
# supports GET


class FollowersApi(Resource):
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str):
        if cache.exists(name + 'followers'):
            return cache.get(name + 'followers'), 200
        else:
            followers_json = json.dumps(get_compact_uinfo(
                User.objects.get(user_name=name).followers))
            cache.set(name + 'followers', followers_json)

            return followers_json, 200
