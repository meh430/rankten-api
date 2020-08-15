from flask import jsonify, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from errors import *
from utils import *
from database.models import User
from database.json_cacher import *

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
        JsonCache.delete(key=user.user_name, itemType=FOLLOWING)
        JsonCache.delete(key=target.user_name, itemType=FOLLOWERS)

        return ('followed user' if exec_follow else 'unfollowed user'), 200

# /following/<name>
# supports GET
class FollowingApi(Resource):
    # returns a list of user's followed by the specified user
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])

        # check if info exists in redis cache
        if not refresh and JsonCache.exists(key=name, itemType=FOLLOWING):
            return jsonify(JsonCache.get_item(key=name, itemType=FOLLOWING))
        else:
            following_json = get_compact_uinfo(User.objects.get(user_name=name).following)
            JsonCache.cache_item(key=name, item=following_json, itemType=FOLLOWING, ex=hours_in_sec(12))

            return following_json, 200

# /followers/<name>
# supports GET
class FollowersApi(Resource):
    @user_does_not_exist_error
    @schema_val_error
    def get(self, name: str):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])

        if not refresh and JsonCache.exists(key=name, itemType=FOLLOWERS):
            return JsonCache.get_item(key=name, itemType=FOLLOWERS), 200
        else:
            followers_json = get_compact_uinfo(User.objects.get(user_name=name).followers)
            JsonCache.cache_item(key=name, item=followers_json, itemType=FOLLOWERS, ex=hours_in_sec(12))

            return followers_json, 200
