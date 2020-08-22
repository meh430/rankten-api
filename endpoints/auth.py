from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from database.models import *
from errors import *
import datetime
import re

name_pattern = "^[a-z0-9_-]{3,15}$"
#Minimum eight characters, at least one upper case English letter, 
#one lower case English letter, one number and one special character
pwd_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$"

# /signup
# supports POST
class SignUpApi(Resource):
    """
    schema:
    {
        "user_name": string,
        "password": string,
        "bio": optional string
    }
    """
    # creates a new user document and return generated jwt token
    @user_already_exists_error
    @schema_val_error
    def post(self):
        body = request.get_json()
        print(body)
        if not re.search(name_pattern, body['user_name']):
            return {'message': 'Username not valid'}, 200

        if not re.search(pwd_pattern, body['password']):
            return {'message': 'Password not valid'}, 200

        user_lists = ListCollection()
        user_lists.save()
        user = User(**body, created_lists=user_lists)
        user.hash_pass()
        user.save()
        user_lists.update(belongs_to=user)
        user_json = user.as_json()
        acc_token = create_access_token(identity=str(
            user.id), expires_delta=datetime.timedelta(days=7))
        user_json['jwt_token'] = acc_token 
        user_json['num_following'] = len(user.following)
        user_json['num_followers'] = len(user.followers)
        return user_json, 200

# /login
# supports POST
class LoginApi(Resource):
    # return newly generated jwt token for login
    """
    schema:
    {
        "user_name": string,
        "password": string
    }
    """
    @user_does_not_exist_error
    @schema_val_error
    def post(self):
        body = request.get_json()
        user = User.objects.get(user_name=body['user_name'])
        auth = user.check_password(body['password'])
        if not auth:
            raise UnauthorizedError

        user_json = user.as_json()
        acc_token = create_access_token(identity=str(
            user.id), expires_delta=datetime.timedelta(days=7))
        user_json['jwt_token'] = acc_token
        user_json['num_following'] = len(user.following)
        user_json['num_followers'] = len(user.followers)
        return user_json, 200

# /validate_token
# supports POST
class TokenApi(Resource):
    # checks token validity
    @jwt_required
    def post(self):
        uid = get_jwt_identity()
        user = User.objects.get(id=uid)
        user_json = user.as_json()
        user_json['num_following'] = len(user.following)
        user_json['num_followers'] = len(user.followers)
        return user_json, 200

#/user_avail/<name>
#supports POST

class UserAvailableApi(Resource):
    #checks if given username is available
    def post(self, name):
        user = User.objects.get(user_name=name)
        if user:
            return {'message': 'Username is taken'}, 200
        else:
            return {'message': 'Username is available'}, 200