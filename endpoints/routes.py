from .auth import SignUpApi, LoginApi
from .users_ep import UsersApi, UserApi
from .ranked_list_ep import RankedListsApi, RankedListApi
from .follow_ep import FollowApi, FollowersApi, FollowingApi
from .discover_ep import DiscoverApi
from .like_ep import LikeApi
from .search_ep import SearchListsApi, SearchUsersApi


def init_routes(api):
    api.add_resource(SignUpApi, '/signup')
    api.add_resource(LoginApi, '/login')

    api.add_resource(UsersApi, '/users')
    api.add_resource(UserApi, '/users/<name>')

    api.add_resource(RankedListsApi, '/rankedlist')
    api.add_resource(RankedListApi, '/rankedlist/<id>')
    api.add_resource(UserRankedListsApi, '/rankedlist/<name>/<page>')

    api.add_resource(FollowApi, '/follow/<name>')
    api.add_resource(FollowersApi, '/followers/<name>')
    api.add_resource(FollowingApi, '/following/<name>')

    api.add_resource(DiscoverApi, '/discover/<page>')

    api.add_resource(LikeApi, '/like/<id>')
    api.add_resource(LikedListsApi, '/likes/<name>/<page>')

    api.add_resource(SearchUsersApi, '/search_users')
    api.add_resource(SearchListsApi, '/search_lists')


def get_slice_bounds(page):
    upper = page * 25
    lower = upper - 25
    return (lower, upper)
