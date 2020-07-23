from .auth import SignUpApi, LoginApi
from .users_ep import UsersApi, UserApi
from .ranked_list_ep import RankedListsApi, RankedListApi


def init_routes(api):
    api.add_resource(SignUpApi, '/signup')
    api.add_resource(LoginApi, '/login')

    api.add_resource(UsersApi, '/users')
    api.add_resource(UserApi, '/users/<id>')

    api.add_resource(RankedListsApi, '/rankedlist')
    api.add_resource(RankedListApi, '/rankedlist/<id>')
