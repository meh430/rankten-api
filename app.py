from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from database.db import init_db
from endpoints.routes import init_routes

app = Flask(__name__)
app.config.from_envvar('ENV_FILE_LOCATION')

api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017'
}

init_db(app)
init_routes(api)

app.run()
