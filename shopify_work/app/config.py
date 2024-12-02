import os
base_dir = os.path.dirname(os.path.abspath(__file__))

class Configs(object):
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "my-secret-key-yayyy"