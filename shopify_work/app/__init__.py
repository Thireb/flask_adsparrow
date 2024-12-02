from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from app.config import Configs

app = Flask(__name__)
app.config.from_object(Configs)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
cors = CORS(app)

from app import api,static