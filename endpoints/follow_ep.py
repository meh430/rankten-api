from flask import Response, request, jsonify
from database.models import User
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from errors import *


class FollowApi(Resource):

    @user_does_not_exist_error
    @schema_val_error
    @internal_server_error
    @jwt_required
    def post(self, name):
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

        return ('followed user' if exec_follow else 'unfollowed user'), 200


class FollowingApi(Resource):
    @schema_val_error
    @internal_server_error
    @user_does_not_exist_error
    def get(self, name):
        following = User.objects.get(user_name=name).following
        return jsonify([{'user_name': f.user_name, 'prof_pic': f.prof_pic, 'rank_points': f.rank_points} for f in following])


class FollowersApi(Resource):
    @schema_val_error
    @internal_server_error
    @user_does_not_exist_error
    def get(self, name):
        followers = User.objects.get(user_name=name).followers
        return jsonify([{'user_name': f.user_name, 'prof_pic': f.prof_pic, 'rank_points': f.rank_points} for f in followers])
