from flask import request, jsonify
from flask import Blueprint
from data.db import get_connection

partidos_bp = Blueprint("partidos", __name__)
