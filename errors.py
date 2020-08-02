from database.db import get_slice_bounds
sort_options = {0: '-num_likes', 1: '-date_created', 2: '+date_created'}


def check_ps(func):
    def wrapper(*args, **kwargs):
        page = int(kwargs['page'])
        sort = int(kwargs['sort']) if 'sort' in kwargs else None

        if page <= 0:
            return 'Invalid page num', 400

        if sort not in sort_options:
            sort = 0

        if 'sort' in kwargs:
            func(*args, page=page, sort=sort, **kwargs)
        else:
            func(*args, page=page, **kwargs)

    return wrapper
