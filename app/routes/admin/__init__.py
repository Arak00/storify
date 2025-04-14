from flask import Blueprint

admin = Blueprint('admin', __name__)

from app.routes.admin import views 