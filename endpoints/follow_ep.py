from flask import jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from errors import *
from database.models import User
from database.json_cacher import *
from endpoints.users_ep import get_compact_uinfo

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
            user.update(push__following=target)
            target.update(push__followers=user)
        else:
            user.update(pull__following=target)
            target.update(pull__followers=user)

        # clear existing redis keys bc they have been updated
        JsonCache.delete(user.user_name + FOLLOWING)
        JsonCache.delete(target.user_name + FOLLOWERS)

        return ('followed user' if exec_follow else 'unfollowed user'), 200

# /following/<name>
# supports GET


class FollowingApi(Resource):
    # returns a list of user's followed by the specified user
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str):
        # check if info exists in redis cache
        if JsonCache.exists(name + FOLLOWING):
            return jsonify(JsonCache.get_item(name + FOLLOWING))
        else:
            following_json = get_compact_uinfo(
                User.objects.get(user_name=name).following)
            JsonCache.cache_item(name + FOLLOWING, following_json)

            return jsonify(following_json)

# /followers/<name>
# supports GET


class FollowersApi(Resource):
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str):
        if JsonCache.exists(name + FOLLOWERS):
            return jsonify(JsonCache.get_item(name + FOLLOWERS))
        else:
            followers_json = get_compact_uinfo(
                User.objects.get(user_name=name).followers)
            JsonCache.cache_item(name + FOLLOWERS, followers_json)

            return jsonify(followers_json)
