from .signup_ep import SignUp
from .users_ep import Users


def init_routes(api):
    api.add_resource(SignUp, '/signup')
    api.add_resource(Users, '/users')
