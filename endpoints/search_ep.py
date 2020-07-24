from flask import Response, request
from flask_restful import Resource
from database.models import User, RankedList


class SearchUsersApi(Resource):
    def get(self):
        query = request.args.get('q')
        result = User.objects(user_name__icontains=query).only(
            'user_name', 'rank_points')

        return Response(result.to_json(), mimetype='application/json', status=200)


class SearchListsApi(Resource):
    # TODO: Query the contents of the list as well
    # TODO: implement sort options like newest, oldest or most liked
    def get(self):
        query = request.args.get('q')
        query = query.replace('+', ' ')

        result = RankedList.objects(title__icontains=query).exclude(
            'created_by', 'liked_users')

        return Response(result.to_json(), mimetype='application/json', status=200)
