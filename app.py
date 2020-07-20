from flask import Flask

app = Flask(__name__)


@app.route('/')
def ping():
    return {'pong': 'HEYA!'}


app.run()
