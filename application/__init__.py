from flask import Flask 
from config import Config 
from flask_mongoengine import MongoEngine

# need to downgrade Werkzeug to use flask_restplus
# pip install Werkzeug==0.16.1

# from flask_restplus import Api
# api = Api()

app = Flask(__name__)
app.config.from_object(Config)

db = MongoEngine()
db.init_app(app)
# api.init_app(app)

from application import routes
