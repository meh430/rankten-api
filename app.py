from flask import Flask
from flask_restful import Api
from database.db import init_db
from endpoints.routes import init_routes

app = Flask(__name__)
api = Api(app)

app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017'
}

init_db(app)
init_routes(api)

app.run()
