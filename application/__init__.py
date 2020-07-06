from flask import Flask 
from config import Config 
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_object(Config)

db = MongoEngine()
db.init_app(app)

# -- API -- 
#  need to downgrade Werkzeug to use flask_restplus
# pip install Werkzeug==0.16.1

from flask import Blueprint
from flask_restplus import Api

blueprint = Blueprint('api', __name__, url_prefix='/v1')
api = Api(blueprint,
            title="Enrollment API",
            version='v0.1',
            description='Enrollment API for CRUD operation'
        )
app.register_blueprint(blueprint)


from application import routes
