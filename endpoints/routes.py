from .auth import *
from .users_ep import *
from .ranked_list_ep import *
from .rank_item_ep import *
from .follow_ep import *
from .discover_ep import *
from .like_ep import *
from .search_ep import *
from .comment_ep import *


def init_routes(api):
    api.add_resource(SignUpApi, '/signup')
    api.add_resource(LoginApi, '/login')
    api.add_resource(TokenApi, '/validate_token')

    api.add_resource(UsersApi, '/users')
    api.add_resource(UserApi, '/users/<name>')

    api.add_resource(RankedListsApi, '/rankedlist')
    api.add_resource(RankedListApi, '/rankedlist/<id>')
    api.add_resource(UserRankedListsApi, '/rankedlists/<name>/<page>/<sort>')
    api.add_resource(UserRankedListsPApi, '/rankedlistsp/<page>/<sort>')

    api.add_resource(RankItemApi, '/rankitem/<id>')
    api.add_resource(BulkUpdateApi, '/rankitems/<id>')

    api.add_resource(FollowApi, '/follow/<name>')
    api.add_resource(FollowersApi, '/followers/<name>')
    api.add_resource(FollowingApi, '/following/<name>')

    api.add_resource(DiscoverApi, '/discover/<page>/<sort>')

    api.add_resource(LikeApi, '/like/<id>')
    api.add_resource(LikeCommentApi, '/like_comment/<id>')
    api.add_resource(LikedListsApi, '/likes/<page>')

    api.add_resource(CommentApi, '/comment/<id>')
    api.add_resource(CommentsApi, '/comments/<id>/<page>/<sort>')
    api.add_resource(UserCommentsApi, '/user_comments/<name>/<page>/<sort>')

    api.add_resource(SearchUsersApi, '/search_users/<page>/<sort>')
    api.add_resource(SearchListsApi, '/search_lists/<page>/<sort>')

    api.add_resource(FeedApi, '/feed/<page>')
