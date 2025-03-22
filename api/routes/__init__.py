from flask import Blueprint

# Tạo Blueprint cho API
api_bp = Blueprint('api', __name__, url_prefix='/api')

from api.routes import user_routes, vps_routes

# Đăng ký các route với blueprint
from api.routes.user_routes import *
from api.routes.vps_routes import * 