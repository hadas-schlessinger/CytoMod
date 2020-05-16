import flask
from .config import Config

app = flask.Flask("__name__", static_folder='app/static')
app.config.from_object(Config)

from app import routes







