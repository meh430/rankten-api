from database.db import get_slice_bounds
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError
sort_options = {0: '-num_likes', 1: '-date_created', 2: '+date_created'}
LIKES_DESC, DATE_DESC, DATE_ASC = 0, 1, 2


class SchemaValidationError(Exception):
    pass


class UserDoesNotExistError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class RankedListUpdateError(Exception):
    pass


class RankedListDeleteError(Exception):
    pass


class RankedListDoesNotExistError(Exception):
    pass


class RankItemUpdateError(Exception):
    pass


class RankItemDeleteError(Exception):
    pass


class RankItemDoesNotExistError(Exception):
    pass


class InvalidPageError(Exception):
    pass


class InvalidSortError(Exception):
    pass


class FollowError(Exception):
    pass


class CommentDoesNotExistError(Exception):
    pass


class CommentUpdateError(Exception):
    pass


class CommentDeleteError(Exception):
    pass


class UnauthorizedError(Exception):
    pass


def check_ps(func):
    def wrapper(*args, **kwargs):
        page = int(kwargs['page'])
        sort = int(kwargs['sort']) if 'sort' in kwargs else None

        if page <= 0:
            raise InvalidPageError

        if sort not in sort_options:
            sort = 0

        if 'name' in kwargs:
            return func(*args, page=page, sort=sort, name=str(kwargs['name']))
        return func(*args, page=page, sort=sort)

    return wrapper


def schema_val_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FieldDoesNotExist, ValidationError, InvalidQueryError, KeyError):
            raise SchemaValidationError

    return wrapper


def user_does_not_exist_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise UserDoesNotExistError

    return wrapper


def user_already_exists_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotUniqueError:
            raise UserAlreadyExistsError

    return wrapper


def list_update_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise RankedListUpdateError

    return wrapper


def list_delete_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise RankedListDeleteError

    return wrapper


def list_does_not_exist_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise RankedListDoesNotExistError

    return wrapper


def rank_update_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise RankItemUpdateError

    return wrapper


def rank_delete_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise RankItemDeleteError

    return wrapper


def rank_does_not_exist_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise RankItemDoesNotExistError

    return wrapper


def comment_does_not_exist_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise CommentDoesNotExistError

    return wrapper


def comment_update_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise CommentUpdateError

    return wrapper


def comment_delete_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DoesNotExist:
            raise CommentDeleteError

    return wrapper


error_dict = {
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
    "SchemaValidationError": {
        "message": "Request is missing required fields",
        "status": 400
    },
    "UserDoesNotExistError": {
        "message": "User with given id or name doesn't exists",
        "status": 400
    },
    "UserAlreadyExistsError": {
        "message": "User with given name or id already exists",
        "status": 400
    },
    "RankedListUpdateError": {
        "message": "Updating list added by other is forbidden",
        "status": 403
    },
    "RankedListDeleteError": {
        "message": "Deleting list added by other is forbidden",
        "status": 403
    },
    "RankedListDoesNotExistError": {
        "message": "List with given id already exists",
        "status": 400
    },
    "RankItemDoesNotExistError": {
        "message": "Rank item with given id does not exist",
        "status": 400
    },
    "RankItemUpdateError": {
        "message": "Updating rank item made by other is forbidden",
        "status": 403
    },
    "RankItemDeleteError": {
        "message": "Deleting ank item made by other is forbidden",
        "status": 403
    },
    "InvalidPageError": {
        "message": "Trying to access a page that does not exist",
        "status": 400
    },
    "InvalidSortError": {
        "message": "Requested sort option does not exist",
        "status": 400
    },
    "FollowError": {
        "message": "Following yourself is forbidden",
        "status": 403
    },
    "CommentDoesNotExistError": {
        "message": "Comment with given id does not exist",
        "status": 400
    },
    "CommentUpdateError": {
        "message": "Updating comment made by other is forbidden",
        "status": 403
    },
    "CommentDeleteError": {
        "message": "Deleting comment made by other is forbidden",
        "status": 403
    },
    "UnauthorizedError": {
        "message": "Invalid username or password",
        "status": 401
    }
}
