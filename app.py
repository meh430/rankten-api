from config import JWT_SECRET_KEY
from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from database.db import init_db
from endpoints.routes import init_routes
from errors import error_dict
from flask_cors import CORS, cross_origin

# TODO: error handling
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['CORS_HEADERS'] = 'Content-Type'

api = Api(app, errors=error_dict)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017'
}


@app.route('/ping')
def method_name():
    return 'PONG!'


init_db(app)
init_routes(api)

app.run(port=5000, host='0.0.0.0')