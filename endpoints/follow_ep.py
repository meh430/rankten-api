from flask import Response, request
from database.models import User
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

# follow: add spec user to following list and add yourself to the user's followers list
# unfollow: rm spec user from folling list and rm yourself from user's followers list


class FollowApi(Resource):
    @jwt_required
    def post(self, name):
        # check if user in following list. If there, that means unfollow, if not, follow
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        other = User.objects.get(user_name=name)
        exec_follow = True
        for follow in user.following:
            if other == follow:
                exec_follow = False
                break

        if exec_follow:
            user.update(push__following=other,
                        following_num=user.following_num+1)
            user.save()
            other.update(push__followers=user,
                         followers_num=other.followers_num + 1)
            other.save()
        else:
            user.update(pull__following=other,
                        following_num=user.following_num - 1)
            user.save()
            other.update(pull__followers=user,
                         followers_num=other.followers_num - 1)

        return ('followed user' if exec_follow else 'unfollowed user'), 200
