from flask import Response, request, jsonify
from database.models import RankedList
from flask_restful import Resource
from database.db import get_slice_bounds


class DiscoverApi(Resource):
    # TODO: implement sort options like newest, oldest or most liked
    def get(self, page):
        lower, upper = get_slice_bounds(page)
        return jsonify(RankedList.objects.exclude('created_by', 'liked_users')[lower:upper])
