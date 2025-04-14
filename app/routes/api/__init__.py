from flask import Blueprint

api = Blueprint('api', __name__)

from app.routes.api import users, sites, products, analytics 