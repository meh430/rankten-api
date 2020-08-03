from flask import jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from errors import *
from database.models import User


class FollowApi(Resource):
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

        return ('followed user' if exec_follow else 'unfollowed user'), 200


class FollowingApi(Resource):
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str):
        return jsonify([{'user_name': f.user_name, 'prof_pic': f.prof_pic, 'rank_points': f.rank_points} for f in User.objects.get(user_name=name).following])


class FollowersApi(Resource):
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str):
        return jsonify([{'user_name': f.user_name, 'prof_pic': f.prof_pic, 'rank_points': f.rank_points} for f in User.objects.get(user_name=name).followers])
