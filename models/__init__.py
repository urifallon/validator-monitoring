from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.vps import VPS 