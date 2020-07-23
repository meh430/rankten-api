from flask import Response, request, jsonify
from database.models import RankedList
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity


class DiscoverApi(Resource):
    def get(self, page):
        upper = page * 25
        lower = upper - 25

        return Response(RankedList.objects.exclude('created_by', 'liked_users')[lower:upper].to_json(), mimetype='application/json', status=200)
