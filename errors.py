from database.db import get_slice_bounds
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist, ValidationError, InvalidQueryError
sort_options = {0: '-num_likes', 1: '-date_created', 2: '+date_created'}


class InternalServerError(Exception):
    pass


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


class InvalidPageError(Exception):
    pass


class InvalidSortError(Exception):
    pass


class FollowError(Exception):
    pass


class CommentDoesNotExistError(Exception):
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

        if 'sort' in kwargs:
            func(*args, page=page, sort=sort, **kwargs)
        else:
            func(*args, page=page, **kwargs)

    return wrapper


def internal_server_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            raise InternalServerError

    return wrapper


def schema_val_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except (FieldDoesNotExist, ValidationError, InvalidQueryError):
            raise SchemaValidationError

    return wrapper


def user_does_not_exist_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except DoesNotExist:
            raise UserDoesNotExistError

    return wrapper


def user_already_exists_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except NotUniqueError:
            raise UserAlreadyExistsError

    return wrapper


def list_update_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except DoesNotExist:
            raise RankedListUpdateError

    return wrapper


def list_delete_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except DoesNotExist:
            raise RankedListDeleteError

    return wrapper


def list_does_not_exist_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except DoesNotExist:
            raise RankedListDoesNotExistError

    return wrapper


def comment_does_not_exist_error(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except DoesNotExist:
            raise CommentDoesNotExistError

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
    "UnauthorizedError": {
        "message": "Invalid username or password",
        "status": 401
    }
}
