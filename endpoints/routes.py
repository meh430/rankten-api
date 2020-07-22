from .auth import SignUpApi, LoginApi
from .users_ep import UsersApi, UserApi


def init_routes(api):
    api.add_resource(SignUpApi, '/signup')
    api.add_resource(LoginApi, '/login')

    api.add_resource(UsersApi, '/users')
    api.add_resource(UserApi, '/users/<id>')
