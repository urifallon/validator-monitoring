from flask import Blueprint

# Tạo Blueprint cho Web interface
web_bp = Blueprint('web', __name__)

from api.web import routes 