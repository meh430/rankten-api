from flask import request, jsonify
from flask_restful import Resource
from database.models import RankedList
from errors import *
from database.json_cacher import *
from utils import *

# /discover/<page>/<sort>
# supports GET
class DiscoverApi(Resource):
    # returns all the lists
    @check_ps
    @schema_val_error
    def get(self, page: int, sort: int):
        refresh = False
        if 're' in request.args:
            refresh = bool(request.args['re'])

        all_lists = []
        if not refresh and JsonCache.exists(key=DISCOVER_LIST, itemType=DISCOVER_LIST, page=page, sort=sort):
            all_lists = JsonCache.get_item(key=DISCOVER_LIST, itemType=DISCOVER_LIST, page=page, sort=sort)
        else:
            bounds = validate_bounds(RankedList.objects.count(), page)
            if not bounds:
                raise InvalidPageError
            
            all_lists = RankedList.objects().order_by(sort_options[sort])[bounds[0]:bounds[1]]
            all_lists = ranked_list_card(all_lists)
            JsonCache.cache_item(key=DISCOVER_LIST, itemType=DISCOVER_LIST, page=page, sort=sort, item=all_lists)

        return all_lists, 200